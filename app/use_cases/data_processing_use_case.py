# app/use_cases/data_processing_use_case.py

import re

level_patterns = {
    1: {
        'elite_house': r'premium class|VIP class|elite house',
        'marble_halls': r'marble halls|marble staircase',
        'design_project_gift': r'design project.*gift',
        'smart_home': r'smart home',
        'sauna': r'sauna',
        'sea_view': r'sea view|direct sea view',
        'panoramic_windows': r'panoramic windows',
        'yacht_club': r'yacht club',
        'spa_complex': r'spa complex',
        'pool': r'pool|swimming pool',
        'marble': r'marble|marble window sills',
        'seaside_area': r'seaside area|Arcadia|French Boulevard',
        'city_center': r'city center|historical center',
        'walking_distance_sea': r'walking distance to.*sea|5 minutes.*sea'
    },
    2: {
        'full_renovation': r'fully renovated|overhaul|high-quality repair|designer renovation|eurorepair|expensive renovation',
        'high_ceilings': r'high ceilings',
        'underground_parking': r'underground parking',
        'guarded_territory': r'closed.*territory|guarded territory|24-hour security',
        'concierge': r'concierge',
        'new_elevator': r'new elevator|high-speed elevators|silent elevators',
        'heated_floors': r'heated floors|warm floors',
        'individual_gas_heating': r'AGV|individual gas heating|2-circuit boiler',
        'brick_house': r'brick house|red brick',
        'new_house': r'new house|recently built|commissioned',
        'parquet': r'parquet|oak parquet',
        'spanish_tiles': r'Spanish tiles',
        'decorative_plaster': r'decorative plaster',
        'natural_wood': r'natural wood|wood doors',
        'fitness_club': r'fitness club',
        'shopping_center': r'shopping center'
    },
    3: {
        'cosmetic_repair': r'cosmetic repairs',
        'glazed_balcony': r'glazed balcony',
        'glazed_loggia': r'glazed loggia|insulated loggia',
        'built_in_kitchen': r'built-in kitchen|wood kitchen',
        'kitchen_studio': r'kitchen-studio|kitchen-living room',
        'fully_furnished': r'fully furnished|all furniture|fully equipped with.*furniture',
        'fully_equipped_appliances': r'appliances included|fully equipped with.*appliances',
        'intercom': r'intercom|code lock',
        'video_surveillance': r'video surveillance|cameras',
        'open_parking': r'open parking|guest parking|parking space',
        'playground': r'playground',
        'supermarket': r'supermarket',
        'school': r'school',
        'kindergarten': r'kindergarten',
        'park': r'park|Victory Park|Shevchenko Park',
        'mpo_windows': r'MPO|reinforced-plastic windows|metal-plastic windows',
        'laminate': r'laminate',
        'quiet_place': r'quiet place|away from roadway',
        'near_park_sanatorium': r'near park|sanatorium'
    },
    4: {
        'living_condition': r'living condition',
        'partly_furnished': r'furniture included',
        'courtyard_view': r'courtyard view|windows overlook.*courtyard',
        'city_view': r'city view',
        'park_view': r'park view|view of.*park',
        'market': r'market|bazaar',
        'clinic_hospital': r'clinic|hospital',
        'transport_interchange': r'transport interchange',
        'cooperative_house': r'cooperative house',
        'redevelopment_possible': r'redevelopment|re-planned|free layout',
        'extra_space': r'extra room|possibility of expansion|attic as a gift',
        'free_storage_room': r'storage room.*gift',
        'installment_plan': r'installment plan'
    },
    5: {
        'needs_renovation': r'needs repair|for renovation',
        'builder_condition': r'condition from builders',
        'commercial_use': r'for commerce',
        'heat_meter': r'heat meter',
        'heat_pumps': r'heat pumps',
        'own_boiler_room': r'own boiler room|roof boiler room',
        'ramp': r'ramp',
        'wheelchair_storage': r'public wheelchair',
        'ecologically_clean_area': r'ecologically clean area',
        'sports_ground': r'sports ground',
        'restaurant_cafe': r'restaurant|coffee shop',
        'terrace': r'terrace|large terrace',
        'bay_window': r'bay window',
        'dressing_room': r'wardrobe|dressing room',
        'storage_room': r'storage room|interfloor storage'
    }
}


# Function to extract features from the description
def extract_features(description):
    if not isinstance(description, str) or not description.strip():
        return {'property_level': 5, 'warning': 'Description is missing, assigned lowest quality level (5)'}

    # Count matches for each level
    level_scores = {level: 0 for level in range(1, 6)}

    for level, patterns in level_patterns.items():
        for feature, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                level_scores[level] += 1

    # Determine the level with the most matches
    max_score = max(level_scores.values())
    if max_score == 0:
        return {'property_level': 5, 'warning': 'No key features found, assigned lowest quality level (5)'}

    # Choose the highest quality level (lowest number) among those with max score
    selected_level = min([level for level, score in level_scores.items() if score == max_score])

    return {'property_level': selected_level}

