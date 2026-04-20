from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from accounts.models import User
from venues.models import Venue
from gigs.models import GigListing, GigApplication


DEMO_PASSWORD = 'demo1234'


class Command(BaseCommand):
    help = 'Seeds the database with demo users, venues, gigs, and applications'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo data...')

        # --- Venue Owners ---
        owner1 = self._make_user('nova_venue', 'Nova', 'Reyes', 'venue_owner',
            bio='Owner of two of Chicago\'s most electric nightlife spots.',
            location='Chicago, IL')

        owner2 = self._make_user('thatch_club', 'Marcus', 'Thatch', 'venue_owner',
            bio='Running the underground scene in Brooklyn since 2015.',
            location='Brooklyn, NY')

        # --- Performers ---
        perf1 = self._make_user('djsolara', 'Solara', 'Kim', 'performer',
            stage_name='DJ Solara',
            music_style='House, EDM',
            bio='Chicago-based DJ spinning house and techno. 8 years on the decks.',
            location='Chicago, IL',
            soundcloud_url='https://soundcloud.com/djsolara',
            instagram_url='https://instagram.com/djsolara')

        perf2 = self._make_user('marcwave', 'Marco', 'Vidal', 'performer',
            stage_name='Marcwave',
            music_style='Hip Hop, Open Format',
            bio='Hip hop DJ and producer. Known for high-energy sets.',
            location='New York, NY',
            soundcloud_url='https://soundcloud.com/marcwave',
            spotify_url='https://open.spotify.com/artist/marcwave',
            instagram_url='https://instagram.com/marcwave')

        perf3 = self._make_user('lunasound', 'Luna', 'Patel', 'performer',
            stage_name='Luna Sound',
            music_style='Acoustic, Live Band',
            bio='Singer-songwriter bringing folk and acoustic vibes to any room.',
            location='Austin, TX',
            spotify_url='https://open.spotify.com/artist/lunasound',
            instagram_url='https://instagram.com/lunasound')

        # --- Fan ---
        self._make_user('gigfan_alex', 'Alex', 'Jordan', 'fan',
            bio='Music lover always looking for the next great show.',
            location='Chicago, IL')

        # --- Venues ---
        venue1 = Venue.objects.get_or_create(
            name='The Nova Room',
            owner=owner1,
            defaults=dict(
                description='A 400-cap underground venue known for its sound system and late-night energy.',
                address='1240 W Randolph St',
                city='Chicago',
                state='IL',
                capacity=400,
                genre_tags='House, EDM, Techno',
            )
        )[0]

        venue2 = Venue.objects.get_or_create(
            name='Pulse Lounge',
            owner=owner1,
            defaults=dict(
                description='Intimate cocktail bar with a strong live music program.',
                address='875 N Milwaukee Ave',
                city='Chicago',
                state='IL',
                capacity=120,
                genre_tags='Acoustic, Jazz, Hip Hop',
            )
        )[0]

        venue3 = Venue.objects.get_or_create(
            name='The Thatch',
            owner=owner2,
            defaults=dict(
                description='Brooklyn\'s favorite underground club. No dress code, great music only.',
                address='214 Morgan Ave',
                city='Brooklyn',
                state='NY',
                capacity=250,
                genre_tags='Hip Hop, Open Format, House',
            )
        )[0]

        # --- Gig Listings ---
        today = date.today()

        g1 = self._make_gig(owner1, venue1, 'Friday Night Residency',
            today + timedelta(days=4), time(22, 0), 350, 'house',
            'Looking for a house DJ for our weekly Friday night slot. 3-hour set.')

        g2 = self._make_gig(owner1, venue2, 'Saturday Acoustic Session',
            today + timedelta(days=9), time(20, 0), 200, 'acoustic',
            'Intimate acoustic set for our Saturday happy hour crowd. 2 hours.')

        g3 = self._make_gig(owner1, venue1, 'New Year\'s Eve Headline',
            today + timedelta(days=21), time(21, 0), 800, 'edm',
            'Headline slot for our NYE party. Big room energy required.')

        g4 = self._make_gig(owner2, venue3, 'Hip Hop Thursday',
            today + timedelta(days=3), time(21, 30), 275, 'hip_hop',
            'Weekly hip hop night. Looking for someone who can read the crowd.')

        g5 = self._make_gig(owner2, venue3, 'Open Format Saturday',
            today + timedelta(days=11), time(23, 0), 400, 'open_format',
            'Open format night — top 40, hip hop, and dance. Keep the floor packed.')

        # Past gig (closed, already happened)
        g6 = self._make_gig(owner1, venue1, 'Halloween Special',
            today - timedelta(days=5), time(22, 0), 500, 'edm',
            'Halloween night main room set.', is_open=False)

        # --- Applications ---
        # g1: Solara accepted, Marcwave pending
        self._apply(perf1, g1, 'House is my bread and butter. I\'ve played this room before and know how to work the crowd.', 'accepted')
        self._apply(perf2, g1, 'I can flex into house when needed — big fan of the venue.', 'pending')

        # g4: Marcwave accepted
        self._apply(perf2, g4, 'Hip hop is my main genre. I\'ve been doing Thursday nights for two years straight.', 'accepted')
        self._apply(perf1, g4, 'I\'d love to branch out into hip hop sets — happy to share a demo mix.', 'declined')

        # g5: pending applications
        self._apply(perf1, g5, 'Open format is where I shine — can blend anything.', 'pending')
        self._apply(perf2, g5, 'My open format sets run 4-5 hours without a dull moment.', 'pending')

        # g6 (past/closed): Solara was booked
        self._apply(perf1, g6, 'Halloween sets are my favorite.', 'accepted')

        # g2: Luna applying
        self._apply(perf3, g2, 'Acoustic sessions are exactly what I do. Happy to share a setlist.', 'pending')

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write('\nDemo accounts (all use password: demo1234):')
        self.stdout.write('  nova_venue   — Venue Owner (2 venues in Chicago)')
        self.stdout.write('  thatch_club  — Venue Owner (1 venue in Brooklyn)')
        self.stdout.write('  djsolara     — Performer (House/EDM)')
        self.stdout.write('  marcwave     — Performer (Hip Hop)')
        self.stdout.write('  lunasound    — Performer (Acoustic)')
        self.stdout.write('  gigfan_alex  — Fan')

    def _make_user(self, username, first, last, role, **kwargs):
        user, created = User.objects.get_or_create(username=username, defaults=dict(
            first_name=first,
            last_name=last,
            role=role,
            **kwargs
        ))
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
            self.stdout.write(f'  Created user: {username}')
        else:
            self.stdout.write(f'  Skipped (exists): {username}')
        return user

    def _make_gig(self, owner, venue, title, event_date, start_time, pay, style, description, is_open=True):
        gig, created = GigListing.objects.get_or_create(
            title=title,
            created_by=owner,
            defaults=dict(
                venue=venue,
                venue_name=venue.name,
                location=f'{venue.city}, {venue.state}',
                event_date=event_date,
                start_time=start_time,
                pay=pay,
                preferred_style=style,
                description=description,
                is_open=is_open,
            )
        )
        if created:
            self.stdout.write(f'  Created gig: {title}')
        return gig

    def _apply(self, performer, listing, message, status):
        app, created = GigApplication.objects.get_or_create(
            performer=performer,
            listing=listing,
            defaults=dict(message=message, status=status)
        )
        if created:
            self.stdout.write(f'  Application: {performer.username} → {listing.title} ({status})')
        return app
