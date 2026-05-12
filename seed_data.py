"""
Seed script — migrates all WordPress blog posts + existing events into the database.
Run: cd 5wof_backend && source venv/bin/activate && python3 seed_data.py
"""
import asyncio
from datetime import datetime
from database import async_session, engine, Base
from models.blog_post import BlogPost
from models.event import Event
from models.contact_submission import ContactSubmission
from models.admin import Admin
import re

def slug(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

BLOG_POSTS = [
    {
        "title": "Echoes of Elegance: The Resurgence of the Mamian Skirt in Contemporary Fashion",
        "author": "Huimin You",
        "category": "Fashion Designers",
        "tags": "blog, dmu, entrepreneurship, fashion, lifestyle, runway, style, trends",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/photo-2025-06-17-23-53-36-2.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/06/18/echoes-of-elegance-the-resurgence-of-the-mamian-skirt-in-contemporary-fashion/",
        "excerpt": "A Cultural classic reimagined for the modern muse – the mamian skirt is experiencing a dynamic revival as designers rediscover its structured beauty and cultural depth.",
        "content": "A Cultural classic reimagined for the modern muse – By Huimin You/July (Wink – Milk)\n\nThe mamian skirt, a time-honored staple in traditional Chinese womenswear, is experiencing a dynamic revival as designers and wearers rediscover its structured beauty and cultural depth. Once a marker of nobility and formality in imperial China, the mamian skirt—named after its resemblance to a horse's face due to its flat front panel—has transcended centuries to find its place in the contemporary fashion landscape.\n\nThis resurgence is not merely a nostalgic return to historical dress, but a creative reimagining that speaks to modern sensibilities. Designers are blending traditional pleating techniques with contemporary fabrics, silhouettes, and styling, creating pieces that honor heritage while embracing innovation.\n\nThe mamian skirt's revival reflects a broader trend in global fashion: the desire to reconnect with cultural roots while pushing creative boundaries. As the fashion industry increasingly values authenticity and storytelling, garments like the mamian skirt offer a powerful narrative of identity, craftsmanship, and cultural continuity.",
        "created_at": "2025-06-18T12:00:00Z",
    },
    {
        "title": "My Disappearing Past",
        "author": "Claudia Adetoro",
        "category": "Fashion Designers",
        "tags": "art, fashion, lifestyle, style, writing",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/photo-2025-06-17-13-25-03.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/06/17/my-disappearing-past/",
        "excerpt": "A tale of fading memories — inspiration from a Nigerian beach town known as 'Eleko,' where childhood memories shape creative vision.",
        "content": "By Claudia Adetoro\n\nA tale of my fading memories\n\nThe primary inspiration for this project stems from a Nigerian beach town known as 'Eleko,' where I spent my early childhood. Born in Nigeria, I lived there until my family moved to England. In the initial stages of my research, I focused on an 'object of desire'—a cherished memory that has shaped my creative identity.\n\nThis collection explores the tension between remembering and forgetting, between the vivid colors of childhood and the muted tones of distant memory. Each piece is designed to evoke the sensation of reaching for something just beyond grasp—a place, a feeling, a moment in time.\n\nThrough fabric manipulation and color gradients, the collection captures the essence of a disappearing past: vibrant at the edges, fading toward the center, yet always present in its influence on who we become.",
        "created_at": "2025-06-17T12:00:00Z",
    },
    {
        "title": "Aso Oke Blazer",
        "author": "Adenike",
        "category": "Fashion Designers",
        "tags": "fashion, heritage, culture",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/photo-2025-06-17-12-50-45-2.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/06/17/aso-oke-blazer/",
        "excerpt": "A statement of power, heritage, and confidence — blending culture, luxury, and empowerment into a single, unforgettable look.",
        "content": "By Adenike\n\nImagine stepping into a room where your presence alone speaks volumes—where what you wear isn't just fabric, but a statement of power, heritage, and confidence. The fabric combines green, gold, and white colours.\n\nAso Oke blazer—a piece that blends culture, luxury, and empowerment into a single, unforgettable look. Aso Oke is a hand-woven cloth that holds deep cultural significance among the Yoruba people of West Africa. Traditionally reserved for important ceremonies and celebrations, it symbolizes prestige, wealth, and community.\n\nBy reimagining this iconic textile as a modern blazer, I bridge the gap between tradition and contemporary fashion. The structured silhouette of the blazer meets the rich texture and vibrant patterns of Aso Oke, creating a garment that commands attention while honoring its cultural origins.\n\nThis piece is for the woman who carries her heritage with pride and wears her confidence like armor.",
        "created_at": "2025-06-17T11:00:00Z",
    },
    {
        "title": "Legendry Living: A Story of Purpose, Values, and Conscious Living",
        "author": "Hayley-Jane Wildsmith",
        "category": "Fashion Designers",
        "tags": "life, mindfulness, personal-growth, spirituality, sustainability",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/photo-2025-06-17-11-58-06.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/06/17/legendry-living-a-story-of-purpose-values-and-conscious-living/",
        "excerpt": "Over the course of a career spanning H.R and Textiles, insights on listening deeply, thinking practically, and creating solutions that support people and purpose.",
        "content": "By Hayley-Jane Wildsmith, Founder\n\nOver the course of my career, I've worked across two sectors that shaped how I see the world: H.R and Textiles. These roles taught me to listen deeply, think practically, and create solutions that support both people and purpose.\n\nBut alongside these professional insights, I've also carried personal values that have guided every decision—values rooted in mindfulness, sustainability, and the belief that what we create should serve a greater good.\n\nLegendry Living is the culmination of these experiences. It's a brand built on the principle that fashion can be both beautiful and conscious, that luxury doesn't require compromise, and that every garment can tell a story of purpose.\n\nThrough carefully sourced materials, ethical production methods, and designs that prioritize longevity over trends, Legendry Living offers a new paradigm for fashion—one where style and substance coexist harmoniously.",
        "created_at": "2025-06-17T10:00:00Z",
    },
    {
        "title": "Adjoavi Style: The Daley Sculptured Gown",
        "author": "Blessing Ukpe",
        "category": "Fashion Designers",
        "tags": "adjoavi-style, fashion, lifestyle, met-gala, style",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/img_6407.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/06/17/adjoavi-style-the-daley-sculptured-gown/",
        "excerpt": "Elevated elegance rooted in culture — the Daley Sculptured Gown represents confidence, purpose, and architectural beauty in deep red velvet.",
        "content": "By Blessing Ukpe\n\nThe Daley Sculptured Gown represents what my brand, Adjoavi Style stands for: elevated elegance rooted in culture, crafted for the woman who moves with confidence and purpose.\n\nThe name \"Daley\" evokes legacy and strength, qualities we honour in every thread. Sculpted in deep red velvet, its bold silhouette and architectural draping are designed to embrace the body while making a powerful visual statement.\n\nEvery curve and fold of this gown has been carefully considered—not just for aesthetic impact, but for the way it makes the wearer feel. Fashion, at its best, is transformative. It doesn't just change how others see you; it changes how you see yourself.\n\nThe Daley Sculptured Gown is an invitation to step into your power, to wear your heritage like a crown, and to move through the world with the grace and authority that comes from knowing exactly who you are.",
        "created_at": "2025-06-17T09:00:00Z",
    },
    {
        "title": "Equestrian",
        "author": "Mine Yeter",
        "category": "Fashion Designers",
        "tags": "art, dmu, entrepreneurship, fashion, history, lifestyle, runway, style",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/05/unnamed-1.png",
        "external_link": "https://rootedinopulence.wordpress.com/2025/05/07/equestrian/",
        "excerpt": "Inspired by a grandfather's farm in Turkey — creating pieces that embody a harmonious blend of functionality, modesty, and sophistication.",
        "content": "By Mine Yeter\n\nThe inspiration for my collection stems from my family, particularly my grandfather's farm in the Besni, Adıyaman province of Turkey. This influence emerged from the loose wool and cotton garments traditionally worn by both men and women on the farm.\n\nI envisioned creating pieces that embody a harmonious blend of functionality, modesty, and sophistication. Embracing these traditional elements, my designs reinterpret rural workwear through the lens of contemporary fashion.\n\nEach garment in the Equestrian collection tells a story of heritage meeting innovation—where the practical wisdom of generations past informs the creative vision of the present. The collection celebrates the beauty found in simplicity, the elegance of functional design, and the timeless appeal of garments made with intention and care.",
        "created_at": "2025-05-07T12:00:00Z",
    },
    {
        "title": "Parting Seas",
        "author": "Funmi Ogundimu",
        "category": "Fashion Designers",
        "tags": "art, books, dmu, entrepreneurship, fashion, runway, writing",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/05/photo-2025-06-17-20-35-04-2.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/05/07/parting-seas/",
        "excerpt": "An exploration of the journey of migrants and asylum seekers — using wet forming of leather off cuts to depict the physical aspects of the journey.",
        "content": "By Funmi Ogundimu\n\nMy Graduate Collection titled Parting Seas is an exploration of the journey of migrants and asylum seekers making their way to England. It draws links from my own personal relationship to immigration.\n\nLooking at the physical aspects of the journey, the project uses the wet forming of leather off cuts, and depicts the textures and movements of the sea—both as barrier and pathway.\n\nThis collection is deeply personal yet universally resonant. It speaks to the courage required to leave everything familiar behind, the uncertainty of the crossing, and the hope that drives people forward even in the face of overwhelming odds.\n\nThrough fashion, I aim to humanize these stories, to give form and beauty to experiences that are too often reduced to statistics. Each piece is a testament to resilience, to the human spirit's capacity to endure and to create beauty even in the midst of hardship.",
        "created_at": "2025-05-07T11:00:00Z",
    },
    {
        "title": "Adufe Lagos",
        "author": "Mariam Oyenuga",
        "category": "Fashion Designers",
        "tags": "dmu, entrepreneurship, fashion, runway",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/05/photo-2025-06-17-20-25-44.jpg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/05/07/adufe-lagos/",
        "excerpt": "Redefining power dressing — blending tradition, artistry, and individuality inspired by the dynamic energy of Lagos.",
        "content": "By Mariam Oyenuga\n\nIn a world where clothing speaks before words ever do, I bring my vision to life through design. At this year's exhibition, I redefine power dressing—blending tradition, artistry, and individuality.\n\nInspired by the dynamic energy of this city, my collection, \"Oba Obinrin\" (Queen in Yoruba), reflects the strength and elegance of every woman who wears it. Lagos is a city of contrasts—vibrant and chaotic, traditional and modern, gentle and fierce.\n\nAdufe Lagos captures these contradictions in fabric and form. Each piece is designed to empower, to remind the wearer of her inherent royalty, and to celebrate the rich cultural tapestry from which we all draw our strength.\n\nThe collection is a love letter to Lagos, to Yoruba heritage, and to every woman who has ever used fashion as a form of self-expression and empowerment.",
        "created_at": "2025-05-07T10:00:00Z",
    },
    {
        "title": "Letter to my Child",
        "author": "Rumbie",
        "category": "Fashion Designers",
        "tags": "entrepreneurship, fashion, runway, writing",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/05/whatsapp-image-2025-06-12-at-13.04.26.jpeg",
        "external_link": "https://rootedinopulence.wordpress.com/2025/05/07/letter-to-my-child-by-rumbie/",
        "excerpt": "HERUNO HALO — a gift from the past come into the present, inspired by a personal journey of embracing femininity in all its richness and complexity.",
        "content": "By Rumbie\n\nHERUNO HALO is a gift from the past come into the present. HERUNO HALO is inspired by my personal journey, as a young Gen Z / Millennial woman, to embracing femininity in all its richness and complexity.\n\nIt's first accessories – coined the 'Portaborse' accessories by a dear Swiss-Italian friend – are an ode to the women who came before us, the mothers and grandmothers whose strength and grace we carry forward.\n\nThis collection is deeply intimate. Each piece tells a story of inheritance—not just of objects, but of values, of dreams, of the quiet strength that passes from one generation to the next.\n\nLetter to my Child is both a look back and a look forward. It honors the past while creating something new, something that will one day be passed on to the next generation as a testament to creativity, love, and the enduring power of fashion to tell our most personal stories.",
        "created_at": "2025-05-07T09:00:00Z",
    },
    {
        "title": "About — Rooted in Opulence",
        "author": "DMU Fashion Exhibition",
        "category": "Fashion Designers",
        "tags": "dmu, fashion, exhibition",
        "cover_image": "https://rootedinopulence.wordpress.com/wp-content/uploads/2025/06/clean-simple-logo.png",
        "external_link": "https://rootedinopulence.wordpress.com/2025/04/14/about/",
        "excerpt": "The official digital exhibition space for the 2025 DMU Fashion Showcase — celebrating creativity, heritage, and innovation of emerging designers.",
        "content": "Rooted in Opulence\n\nWelcome to Rooted in Opulence, the official digital exhibition space for the 2025 DMU Fashion Showcase. This platform celebrates the creativity, heritage, and innovation of emerging designers from De Montfort University's Fashion School.\n\nEach piece you'll discover here is more than just fabric and form — it's a story of identity, culture, and creative vision. Our designers draw inspiration from their diverse backgrounds, personal experiences, and cultural heritage to create collections that push boundaries and challenge conventions.\n\nRooted in Opulence is not just an exhibition—it's a movement. It represents the next generation of fashion designers who believe that style and substance can coexist, that heritage and innovation are not opposites but partners, and that fashion at its best is a powerful form of storytelling.\n\nWe invite you to explore, to be inspired, and to discover the extraordinary talent that is shaping the future of fashion.",
        "created_at": "2025-04-14T12:00:00Z",
    },
]

EVENTS = [
    {
        "title": "Stating the obvious: a focus on the regression in the quality of Zara",
        "description": "Over the past decade, the Spanish retailer ZARA has faced increasing criticism for its rapid production cycles and declining quality standards.",
        "event_date": "Spring 2026 · Arsh Gill",
        "badge": "Featured",
        "author": "Arsh Gill",
        "external_link": "https://www.linkedin.com/posts/5wof_fastfashion-fashionindustry-fashioncommentator-activity-7452662490435452928-FavQ",
        "link_text": "Read full article",
        "is_published": True,
    },
    {
        "title": "The Lumbers Sustainability Showcase",
        "description": "SDG expert Dr Mark Charlton keynoted this sell-out event at one of Leicester's finest jewellers.",
        "event_date": "2024 · Lumbers Case Study",
        "badge": "Past Event",
        "author": "5Ws Team",
        "external_link": "https://www.linkedin.com/posts/rumbiemakonise-1265b81aa_fashionmanagementwithmarketing-sustainablefashion-ugcPost-7343680058751901697-0EdA",
        "link_text": "View recap",
        "is_published": True,
    },
    {
        "title": "Samia presents at Future Scan 6",
        "description": "Sustainable luxury · Brands · Storytelling",
        "event_date": "2025 · Samia Irshad",
        "badge": "Internal Spotlight",
        "author": "Samia Irshad",
        "external_link": "https://www.linkedin.com/posts/samiairshad_futurescan6-sustainableluxury-storytelling-activity-7376525909140447232-Mz1K",
        "link_text": "View post",
        "is_published": True,
    },
]

async def seed():
    async with async_session() as db:
        # Seed blog posts
        for p in BLOG_POSTS:
            post = BlogPost(
                title=p["title"],
                slug=slug(p["title"]),
                excerpt=p["excerpt"],
                content=p["content"],
                cover_image=p.get("cover_image"),
                author=p["author"],
                category=p["category"],
                tags=p.get("tags"),
                external_link=p.get("external_link"),
                is_published=True,
            )
            db.add(post)
        
        # Seed events
        for e in EVENTS:
            event = Event(**e)
            db.add(event)
        
        await db.commit()
        print(f"Seeded {len(BLOG_POSTS)} blog posts and {len(EVENTS)} events")

if __name__ == "__main__":
    asyncio.run(seed())
