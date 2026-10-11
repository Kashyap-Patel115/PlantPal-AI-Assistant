"""
plant_library.py - Reference Botanical Guide for PlantPal
==========================================================
Provides curated, locally-stored care guides for 7 popular home plants:
1. Money Plant / Pothos
2. Snake Plant (Sansevieria)
3. Aloe Vera
4. Spider Plant
5. Peace Lily
6. Tulsi (Holy Basil)
7. Areca Palm

Users can browse these guides and instantly add them to their personal garden!
"""

LIBRARY_PLANTS = [
    {
        "id": "money-plant",
        "name": "Money Plant",
        "species": "Epipremnum aureum (Golden Pothos)",
        "sunlight": "Indirect Light",
        "sunlight_detail": "Thrives in medium to bright indirect sunlight. Avoid harsh afternoon direct sun which scorches leaves.",
        "watering_interval_days": 7,
        "watering_detail": "Water once every 7 days or whenever the top 1–2 inches of soil feel dry. Drooping vines indicate thirst.",
        "difficulty": "Very Easy",
        "temperature": "18°C – 30°C",
        "benefits": "NASA-rated air purifier, easy to propagate in water or soil, brings vibrant trailing greenery.",
        "care_tips": "Wipe broad leaves with a damp cloth monthly to remove dust. Snip long runners to encourage bushier growth.",
        "common_issues": "Yellow leaves usually mean overwatering; dry brown tips indicate low humidity or underwatering.",
        "icon": "leaf"
    },
    {
        "id": "snake-plant",
        "name": "Snake Plant",
        "species": "Sansevieria trifasciata (Dracaena trifasciata)",
        "sunlight": "Low to Bright Indirect",
        "sunlight_detail": "Extremely adaptable. Survives in dark corners as well as near bright sunny windows.",
        "watering_interval_days": 14,
        "watering_detail": "Water sparingly every 14–21 days. Soil MUST be completely dry before re-watering. Prone to root rot if overwatered.",
        "difficulty": "Indestructible (Beginner)",
        "temperature": "15°C – 32°C",
        "benefits": "Releases oxygen during the night, eliminates airborne toxins like benzene and formaldehyde.",
        "care_tips": "Use well-draining succulent/cactus potting mix. Do not let water sit in the central rosette leaves.",
        "common_issues": "Soft, mushy, yellowing leaf bases indicate root rot from overwatering. Cease watering immediately.",
        "icon": "shield"
    },
    {
        "id": "aloe-vera",
        "name": "Aloe Vera",
        "species": "Aloe barbadensis miller",
        "sunlight": "Bright Direct Sun",
        "sunlight_detail": "Requires 4–6 hours of bright light or direct sunshine daily on a sunny windowsill or balcony.",
        "watering_interval_days": 14,
        "watering_detail": "Soak deeply every 2–3 weeks, then let the soil dry out completely. Reduce watering even further in winter.",
        "difficulty": "Easy",
        "temperature": "13°C – 28°C",
        "benefits": "Fresh medicinal gel soothes minor burns, cuts, and sunburns. Drought-hardy succulent.",
        "care_tips": "Plant in a porous terracotta pot with cactus mix or sandy soil. Never let roots sit in standing water.",
        "common_issues": "Brown, soft leaves indicate too much moisture. Pale or thin leaves mean inadequate sunlight.",
        "icon": "droplet"
    },
    {
        "id": "spider-plant",
        "name": "Spider Plant",
        "species": "Chlorophytum comosum",
        "sunlight": "Bright Indirect",
        "sunlight_detail": "Prefers bright, filtered daylight. Direct sun may bleach or burn the striped foliage.",
        "watering_interval_days": 6,
        "watering_detail": "Water evenly about once a week. Keep soil slightly moist in spring and summer, drier in winter.",
        "difficulty": "Easy",
        "temperature": "15°C – 25°C",
        "benefits": "Non-toxic and 100% safe for cats and dogs! Produces cute cascading baby plantlets (spiderettes).",
        "care_tips": "Repot every 1–2 years when tuberous roots fill the pot. Clip baby plantlets and root them in water.",
        "common_issues": "Brown leaf tips often come from fluoride or chlorine in tap water; use filtered or rested water.",
        "icon": "sprout"
    },
    {
        "id": "peace-lily",
        "name": "Peace Lily",
        "species": "Spathiphyllum wallisii",
        "sunlight": "Medium to Low Light",
        "sunlight_detail": "Prefers shady or low-light spots indoors. Direct sunlight will scorch the delicate white spathes and foliage.",
        "watering_interval_days": 5,
        "watering_detail": "Water every 5–7 days when the soil surface is dry. Peace lilies dramatically droop when thirsty and perk up quickly after a drink.",
        "difficulty": "Moderate",
        "temperature": "18°C – 26°C",
        "benefits": "Elegant white blooms, increases indoor humidity, absorbs airborne mold spores and chemical vapors.",
        "care_tips": "Keep away from cold drafts or air-conditioning vents. Mist leaves weekly for pleasant humidity.",
        "common_issues": "Yellowing leaves can be caused by soggy soil or over-fertilization. Blackened leaves suggest over-chilling.",
        "icon": "flower"
    },
    {
        "id": "tulsi",
        "name": "Tulsi (Holy Basil)",
        "species": "Ocimum tenuiflorum / sanctum",
        "sunlight": "Full Direct Sun",
        "sunlight_detail": "Needs 4–6 hours of direct sunlight daily. Best placed on balconies, sunny verandas, or south-facing windows.",
        "watering_interval_days": 3,
        "watering_detail": "Water every 2–3 days in warm weather. Keep the topsoil lightly moist but well-drained. Water at soil level in early mornings.",
        "difficulty": "Easy to Moderate",
        "temperature": "20°C – 35°C",
        "benefits": "Revered sacred herb with rich Ayurvedic healing properties. Natural mosquito repellent and herbal tea favorite.",
        "care_tips": "Pinch off flower buds (manjari) regularly to encourage bushy, leafy green growth and prevent woodiness.",
        "common_issues": "Leaf drop in winter or cold drafts. Powdery mildew can occur if foliage is sprayed in the dark.",
        "icon": "sun"
    },
    {
        "id": "areca-palm",
        "name": "Areca Palm",
        "species": "Dypsis lutescens (Butterfly Palm)",
        "sunlight": "Bright Filtered Light",
        "sunlight_detail": "Flourishes in bright, filtered daylight. Direct scorching midday sunlight can turn fronds yellow-brown.",
        "watering_interval_days": 6,
        "watering_detail": "Water every 5–7 days. Allow the top inch of soil to dry out between waterings. Sensitive to heavy mineral deposits.",
        "difficulty": "Moderate",
        "temperature": "18°C – 28°C",
        "benefits": "Adds tropical elegance, acts as a natural humidifier, rated highly by NASA for clean indoor air.",
        "care_tips": "Feed with diluted balanced liquid houseplant fertilizer in spring and summer. Prune older browning fronds at base.",
        "common_issues": "Tips turning brown is a common sign of dry indoor air or tap water minerals. Increase humidity or mist lightly.",
        "icon": "palmtree"
    }
]


def get_all_library_plants():
    """Return all plants in the reference library."""
    return LIBRARY_PLANTS


def get_library_plant(plant_id):
    """Find a specific library plant by id slug."""
    for p in LIBRARY_PLANTS:
        if p["id"] == plant_id:
            return p
    return None
