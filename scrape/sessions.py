from django.conf import settings

from service.scraper.base import BaseShopScraper
from service.scraper.ebay import EbayScraper
from main.models import SourceName

class SessionManager:
    _instance = None
    _sessions = dict()
    _session_classes = {
        'ebay': EbayScraper
    }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def _get_free_session(cls, scraper_type):
        instance = cls.get_instance()
        sessions_list = instance._sessions.get(scraper_type, [])

        for i in sessions_list:
            if not i.is_running:
                return i
            
    @classmethod
    def _create_session(cls, scraper_type):
        instance = cls.get_instance()
        sessions_list = instance._sessions.get(scraper_type, [])

        new_session = instance._session_classes[scraper_type](**settings.SCRAPER_OPTIONS)
        new_session.start()

        sessions_list.append(new_session)

        instance._sessions[scraper_type] = sessions_list
        return new_session
    
    @classmethod
    def _cleanup_sessions(cls):
        instance = cls.get_instance()
        for v in instance._sessions.values():
            while len(v) > 1:
                v[-1].quit()
                v.pop()

    @classmethod
    def run_session(cls, scraper_type, action, *args, **kwargs):
        instance = cls.get_instance()
        free_session = instance._get_free_session(scraper_type)
        if free_session is None:
            free_session = instance._create_session(scraper_type)
        
        return free_session.run_action(action, *args, **kwargs)