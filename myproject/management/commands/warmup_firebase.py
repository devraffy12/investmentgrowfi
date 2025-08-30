"""
Django management command to warm up Firebase
"""
from django.core.management.base import BaseCommand
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Warm up Firebase connections to reduce first-request latency'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout in seconds for warmup operations'
        )
    
    def handle(self, *args, **options):
        timeout = options['timeout']
        
        self.stdout.write("🔥 Starting Firebase warmup...")
        start_time = time.perf_counter()
        
        try:
            # Import Firebase modules
            from myproject.firebase_app import get_firebase_app
            from firebase_admin import firestore, db as firebase_db
            
            # Initialize Firebase app
            self.stdout.write("🔥 Initializing Firebase app...")
            app = get_firebase_app()
            
            # Initialize Firestore client
            self.stdout.write("🔥 Initializing Firestore client...")
            firestore_client = firestore.client(app=app)
            
            # Initialize Realtime Database
            self.stdout.write("🔥 Initializing Realtime Database...")
            db_ref = firebase_db.reference('/', app=app)
            
            # Test operations
            self.stdout.write("🔥 Testing Firebase connections...")
            
            # Test Firestore
            try:
                test_doc = firestore_client.collection('_warmup').document('test')
                test_doc.set({'timestamp': time.time(), 'warmup': True})
                test_doc.get()
                self.stdout.write("✅ Firestore connection OK")
            except Exception as e:
                self.stdout.write(f"⚠️ Firestore test failed: {e}")
            
            # Test Realtime Database
            try:
                db_ref.child('_warmup').set({'timestamp': time.time(), 'warmup': True})
                db_ref.child('_warmup').get()
                self.stdout.write("✅ Realtime Database connection OK")
            except Exception as e:
                self.stdout.write(f"⚠️ Realtime Database test failed: {e}")
            
            # Start Firebase queue
            from myproject.firebase_queue import start_firebase_queue
            start_firebase_queue()
            self.stdout.write("✅ Firebase queue started")
            
            duration = (time.perf_counter() - start_time) * 1000
            self.stdout.write(
                self.style.SUCCESS(f"🔥 Firebase warmup completed in {duration:.1f}ms")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Firebase warmup failed: {e}")
            )
            raise
