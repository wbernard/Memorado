project(
  'memorado',
  version: '0.3',
  meson_version: '>= 0.62.0',
  license: 'GPL-3.0-or-later',
)

i18n = import('i18n')
python = import('python')
gnome = import('gnome')


project_id = 'im.bernard.Memorado'
project_name = 'Memorado'
package_url = 'https://github.com/wbernard/Memorado'
issue_url = 'https://github.com/wbernard/Memorado/issues/new'
translate_url = 'https://github.com/wbernard/Memorado/tree/main/po'
copyright = '© 2023 Felipe Kinoshita \n© 2024 Memorado developers'
contributors = '\n'.join([
  'Felipe Kinoshita https://fkinoshita.gitlab.io',
  'Walter Bernard https://walter.bernard.im',
  'Valentin Bernard',
  'Tobias Bernard https://tobiasbernard.com',
])
designers = '\n'.join([
  'Tobias Bernard https://tobiasbernard.com',
])
artists = '\n'.join([
  'Tobias Bernard https://tobiasbernard.com',
])

dependency('gtk4', version: '>=4.9')
dependency('libadwaita-1', version: '>=1.2')

DATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

# Profiles
application_id = project_id
if get_option('profile') == 'development'
    profile = 'Devel'
    application_id = '@0@.Devel'.format(application_id)

    find_program('git')
    rev_txt = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
    version = meson.project_version() + '-' + rev_txt
else
    profile = ''
    version = meson.project_version()
endif


top_source_dir = meson.current_source_dir()
gettext_package = meson.project_name()

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
