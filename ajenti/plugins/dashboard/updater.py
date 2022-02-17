import gevent

from ajenti.api import *
from ajenti.plugins.packages.api import PackageManager, PackageInfo


@plugin
class AjentiUpdater (BasePlugin):
    AJENTI_PACKAGE_NAME = 'ajenti'

    def run_update(self, packages):
        packages = packages or [self.AJENTI_PACKAGE_NAME]
        actions = []
        mgr = PackageManager.get()
        for name in packages:
            p = PackageInfo()
            p.name, p.action = name, 'i'
            actions.append(p)
        mgr.do(actions)

    def check_for_updates(self, callback):
        try:
            mgr = PackageManager.get()
        except NoImplementationsError:
            return

        def worker():
            mgr.refresh()
            r = [
                p.name
                for p in mgr.upgradeable
                if p.name.startswith(self.AJENTI_PACKAGE_NAME)
            ]

            callback(r)

        gevent.spawn(worker)
