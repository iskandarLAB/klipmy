from django.core.management.base import BaseCommand
from submissions.models import ClipSubmission
from submissions.services import update_submission_views

class Command(BaseCommand):
    help = 'Menjalankan semakan automatik tontonan (views) bagi semua video TikTok & Instagram Reels yang aktif'

    def handle(self, *args, **options):
        active_submissions = ClipSubmission.objects.filter(
            status='approved',
            campaign__status='active'
        ).select_related('campaign', 'clipper')

        total = active_submissions.count()
        self.stdout.write(self.style.NOTICE(f"Memulakan scraper tontonan untuk {total} video aktif..."))

        success_count = 0
        for sub in active_submissions:
            try:
                update_submission_views(sub)
                self.stdout.write(self.style.SUCCESS(
                    f"✓ [{sub.platform.upper()}] ID #{sub.id} ({sub.clipper.username}): {sub.verified_views:,} views -> RM {sub.earnings}"
                ))
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"✗ Gagal kemas kini ID #{sub.id}: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Selesai! Sebanyak {success_count}/{total} video berjaya disemak & dikemas kini ganjaran."
        ))
