import folium

from pokemon_entities.models import Pokemon, PokemonEntity
from django.core.exceptions import ObjectDoesNotExist
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
        pokemon_type = Pokemon.objects.get(id=int(pokemon_id))
    except Pokemon.DoesNotExist:
        raise Http404('Pokemon does not exist')
    pokemon_type_parameters = {
        'pokemon_id': pokemon_type.id,
        'img_url': pokemon_type.photo.url,
        'title_ru': pokemon_type.title,
        'title_en': pokemon_type.title_en,
        'title_jp': pokemon_type.title_jp,
        'description': pokemon_type.description
    }
    if not pokemon_type.next_evolutions.all():
        pokemon_type_parameters.update(
            {'previous_evolution': {
                'title_ru': pokemon_type.previous_evolution.title,
                'pokemon_id': pokemon_type.previous_evolution.id,
                'img_url': pokemon_type.previous_evolution.photo.url}
            }
        )

    if not pokemon_type.previous_evolution:
        starter_pokemon = pokemon_type.next_evolutions.all().first()
        pokemon_type_parameters.update(
            {'next_evolution': {
                'title_ru': starter_pokemon.title,
                'pokemon_id': starter_pokemon.id,
                'img_url': starter_pokemon.photo.url}
            }
        )

    if pokemon_type.previous_evolution and pokemon_type.next_evolutions.all():
        pokemon_type_parameters.update(
            {'previous_evolution': {
                    'title_ru': pokemon_type.previous_evolution.title,
                    'pokemon_id': pokemon_type.previous_evolution.id,
                    'img_url': pokemon_type.previous_evolution.photo.url},
                'next_evolution': {
                    'title_ru': pokemon_type.next_evolutions.all().first().title,
                    'pokemon_id': pokemon_type.next_evolutions.all().first().id,
                    'img_url': pokemon_type.next_evolutions.all().first().photo.url}
            }
        )

    requested_pokemons = pokemon_type.pokemon_specie.all()
    if requested_pokemons:
        folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
        for pokemon in requested_pokemons:
            add_pokemon(
                folium_map, pokemon.latitude,
                pokemon.longitude,
                pokemon.pokemon.photo.path
            )
    else:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_type_parameters
    })
