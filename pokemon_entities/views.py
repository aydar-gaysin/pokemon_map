import folium

from pokemon_entities.models import Pokemon, PokemonEntity
from django.http import Http404
from django.http import HttpResponseNotFound
from django.shortcuts import render

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
    try:
        pokemon = Pokemon.objects.get(id=int(pokemon_id))
    except Pokemon.DoesNotExist:
        raise Http404('Pokemon does not exist')
    pokemon_parameters = {
        'pokemon_id': pokemon.id,
        'img_url': pokemon.photo.url,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description
    }
    if not pokemon.next_evolutions.all():
        pokemon_parameters.update(
            {'previous_evolution': {
                'title_ru': pokemon.previous_evolution.title,
                'pokemon_id': pokemon.previous_evolution.id,
                'img_url': pokemon.previous_evolution.photo.url}
            }
        )

    if not pokemon.previous_evolution:
        starter_pokemon = pokemon.next_evolutions.all().first()
        pokemon_parameters.update(
            {'next_evolution': {
                'title_ru': starter_pokemon.title,
                'pokemon_id': starter_pokemon.id,
                'img_url': starter_pokemon.photo.url}
            }
        )

    entities = pokemon.pokemons.all()
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entitiy in entities:
        add_pokemon(
            folium_map, entitiy.latitude,
            entitiy.longitude,
            entitiy.pokemon.photo.path
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_parameters
    })
