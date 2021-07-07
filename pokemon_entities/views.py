import folium
import json

from pokemon_entities.models import Pokemon, PokemonEntity
from django.http import HttpResponseNotFound
from django.shortcuts import render
from itertools import count

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    pokemon_entities = PokemonEntity.objects.all()
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.latitude,
            pokemon_entity.longitude,
            pokemon_entity.pokemon.photo.path
        )

    pokemons_model = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemons_model:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': pokemon.photo.url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    certain_pokemon = Pokemon.objects.get(id=int(pokemon_id))
    if certain_pokemon.previous_evolution:
        certain_pokemon_data = {
                'pokemon_id': certain_pokemon.id,
                'img_url': certain_pokemon.photo.url,
                'title_ru': certain_pokemon.title,
                'title_en': certain_pokemon.title_en,
                'title_jp': certain_pokemon.title_jp,
                'description': certain_pokemon.description,
                'previous_evolution': {
                    'title_ru': certain_pokemon.previous_evolution.title,
                    'pokemon_id': certain_pokemon.previous_evolution.id,
                    'img_url': certain_pokemon.previous_evolution.photo.url
            }
        }
    else:
        certain_pokemon_data = {
            'pokemon_id': certain_pokemon.id,
            'img_url': certain_pokemon.photo.url,
            'title_ru': certain_pokemon.title,
            'title_en': certain_pokemon.title_en,
            'title_jp': certain_pokemon.title_jp,
            'description': certain_pokemon.description,
        }


    requested_pokemon = PokemonEntity.objects.filter(pokemon__id=int(pokemon_id))
    if requested_pokemon:
        folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
        for pokemon in requested_pokemon:
            add_pokemon(
                folium_map, pokemon.latitude,
                pokemon.longitude,
                pokemon.pokemon.photo.path
            )
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': certain_pokemon_data
    })
