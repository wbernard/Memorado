moduledir = join_paths(DATA_DIR, 'memorado')

const = configuration_data()
const.set('PYTHON', python.find_installation('python3').full_path())
const.set('APPID', application_id)
message(application_id)
const.set('PROFILE', profile)

configure_file(
  input: 'const.py.in',
  output: 'const.py',
  configuration: const,
  install_dir: moduledir,
  install: true
)

conf = configuration_data()

conf.set('VERSION', version)
conf.set('APPID', application_id)
conf.set('GETTEXT_PACKAGE', meson.project_name())
conf.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
conf.set('NAME', project_name)
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('DATA_DIR', DATA_DIR)

configure_file(
  input: 'memorado.in',
  output: 'memorado',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

memorado_sources = [
  '__init__.py',
  'main.py',
  'shared.py',
  'application.py',
  'window.py',
  'welcome.py',
  'list_view.py',
  'deck_view.py',
  'card_view.py',
  'card_new_view.py',
  'deck_row.py',
  'card_row.py',
  'card_edit.py',
]

install_data(memorado_sources, install_dir: moduledir)
