__import__('pkg_resources').declare_namespace(__name__)


class ApplicationFactory(object):

    def create_configuration(self, settings):
        from pyramid.config import Configurator
        from pyramid.authentication import AuthTktAuthenticationPolicy
        from pyramid.authorization import ACLAuthorizationPolicy
        from pyramid_beaker import session_factory_from_settings
        from pyramid_beaker import set_cache_regions_from_settings
        from lxneng.factories import RootFactory
        from lxneng.factories import get_user

        set_cache_regions_from_settings(settings)

        config = Configurator(settings=settings,
                              session_factory=session_factory_from_settings(
                                  settings),
                              root_factory=RootFactory,
                              authentication_policy=AuthTktAuthenticationPolicy(
                                  'secret'),
                              authorization_policy=ACLAuthorizationPolicy()
                              )
        config.set_request_property(get_user, 'user', reify=True)

        return config

    def setup_jinja2(self, config):
        from pyramid_jinja2 import renderer_factory
        config.add_translation_dirs('lxneng:locale')
        config.add_renderer('.html', renderer_factory)

    def setup_static_files(self, config, settings):
        from lxneng.models.photo import Photo
        Photo.root_path = settings['photos_dir']

        if settings.get('asset_url', 0):
            config.add_static_view(
                settings['asset_url'], 'lxneng:static')
        else:
            config.add_static_view(
                'static', 'lxneng:static', cache_max_age=3600)

        if settings.get('photos_url', 0):
            config.add_static_view(
                settings['photos_url'], settings['photos_dir'])
        else:
            config.add_static_view(
                'photos', settings['photos_dir'], cache_max_age=3600)

        if settings.get('images_url', 0):
            config.add_static_view(
                settings['images_url'], settings['images_dir'])
        else:
            config.add_static_view(
                'images', settings['images_dir'], cache_max_age=3600)

    def setup_routes(self, config, settings):
        from lxneng import factories

        config.add_route('home', '/')
        config.add_route('login', '/login')
        config.add_route('logout', '/logout')
        config.add_route('about', '/about')

        # photos
        config.add_route('photos', '/photos')
        config.add_route('all_photos', '/photos/all')
        config.add_route('all_photos_pagination', '/photos/all/{page:\d+}')
        config.add_route('photos_album', '/photos/albums/{id:\d+}',
                         factory=factories.AlbumFactory)
        config.add_route('photos_album_new', '/photos/albums/new')
        config.add_route('photos_album_edit', '/photos/albums/{id:\d+}/edit',
                         factory=factories.AlbumFactory)
        config.add_route(
            'photos_album_upload', '/photos/albums/{id:\d+}/upload',
            factory=factories.AlbumFactory)

        # posts
        config.add_route('posts_index', '/posts')
        config.add_route('posts_archive', '/posts/archive')
        config.add_route('posts_new', '/posts/new')
        config.add_route('posts_tags_index', '/posts/tags')
        config.add_route('posts_rss', '/posts/rss')
        config.add_route('posts_show', '/posts/{id:\d+}',
                         factory=factories.PostFactory)
        config.add_route('posts_edit', '/posts/{id:\d+}/edit',
                         factory=factories.PostFactory)
        config.add_route('posts_delete', '/posts/{id:\d+}/delete')
        config.add_route('posts_tags_show', '/posts/tags/{name}',
                         factory=factories.tag_factory)
        config.add_route('uploader', '/uploader')

        config.add_route('cse', '/search')

    def configure(self, settings):
        config = self.create_configuration(settings)
        self.setup_jinja2(config)
        self.setup_static_files(config, settings)
        self.setup_routes(config, settings)
        config.scan()
        return config

    def __call__(self, global_config, **settings):
        config = self.configure(settings)
        return config.make_wsgi_app()


app_factory = ApplicationFactory()


def main(global_config, **settings):
    return app_factory(global_config, **settings)
