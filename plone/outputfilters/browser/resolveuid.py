from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.browser import BrowserView

try:
    from plone.app.uuid.utils import uuidToURL
except ImportError:
    from zope.app.component.hooks import getSite
    from Products.CMFCore.utils import getToolByName
    def uuidToURL(uuid):
        catalog = getToolByName(getSite(), 'portal_catalog')
        res = catalog(UID=uuid)
        if res:
            return res[0].getObject()


class ResolveUIDView(BrowserView):
    """Resolve a URL like /resolveuid/<uuid> to a normalized URL.
    """
    implements(IPublishTraverse)
    
    def publishTraverse(self, request, name):
        uuid = name
        url = uuidToURL(uuid)
        
        if not url:
            hook = getattr(self.context, 'kupu_resolveuid_hook', None)
            if hook:
                obj = hook(uuid)
            if not obj:
                raise NotFound("The link you followed appears to be broken")
            url = obj.absolute_url()

        traverse_subpath = self.request['TraversalRequestNameStack']
        if traverse_subpath:
            url = '/'.join([url] + traverse_subpath)
            self.request['TraversalRequestNameStack'] = []

        if self.request.QUERY_STRING:
            url += '?' + self.request.QUERY_STRING

        self.request.response.redirect(url, status=301)
        return self

    def __call__(self):
        return ''
