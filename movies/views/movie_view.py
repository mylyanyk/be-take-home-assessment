import json
import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from movies.models.movie_model import MovieModel
from movies.serializers.movie_serializer import MovieSerializer


class MovieViewSet(ModelViewSet):
    serializer_class = MovieSerializer
    queryset = MovieModel.objects.all()

    @action(detail=False, methods=['get', 'post'], url_path='load_external_data')
    def load_external_data(self, request):
        json_file_path = os.path.join(settings.BASE_DIR, 'movies', 'data', 'movies_api_response.json')

        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)

            movies_data = data.get('movies', [])
            created_count = 0
            updated_count = 0

            for movie_data in movies_data:
                if not movie_data.get('title'):
                    continue

                _, created = MovieModel.objects.get_or_create(
                    title=movie_data['title'],
                    release_date=movie_data.get('release_date'),
                    defaults={
                        'genres': movie_data.get('genres', []),
                        'director': movie_data.get('director', ''),
                        'cast': movie_data.get('cast', []),
                        'description': movie_data.get('description', ''),
                        'rating': movie_data.get('rating'),
                        'duration_minutes': movie_data.get('duration_minutes'),
                        'poster_url': movie_data.get('poster_url', ''),
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            return Response({
                'status': 'success',
                'message': f'Created {created_count} and updated {updated_count} movies',
                'created': created_count,
                'updated': updated_count
            }, status=status.HTTP_201_CREATED)

        except FileNotFoundError:
            return Response({
                'status': 'error',
                'message': 'Movies data file not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({
                'status': 'error',
                'message': 'Invalid JSON format'
            }, status=status.HTTP_400_BAD_REQUEST)
