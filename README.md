<h1 align="center">
  <img src="data/icons/hicolor/scalable/apps/im.bernard.Memorado.svg" alt="Memorado app icon" width="192" height="192"/>
  <br>
  Memorado
</h1>

<p align="center"><strong>Memorize anything</strong></p>

<p align="center">
  <img src="/data/screenshots/decks.png" alt="List of decks"/>
  <img src="/data/screenshots/edit-deck.png" alt="Edit cards in a deck"/>
  <img src="/data/screenshots/practice.png" alt="Practice with cards"/>
</p>

Learn using spaced repetition. Create cards with a question and answer, and practice with them.

## Database layout

- cards
    - deck_id   (TEXT)
    - front     (TEXT)
    - back      (TEXT)
- decks
    - deck_id   (TEXT)
    - name      (TEXT)
    - icon      (TEXT)

deck_id: uuid created on initialisation

## Translations

Update the `.pot` file when strings in the app change:

- Open a "Build terminal" in Builder from the + menu in the top left
- Run `ninja memorado-pot`

Update the individual `.po` files with new strings:

- Open a "Build terminal" in Builder from the + menu in the top left
- Run `ninja memorado-update-pot`

## Code of conduct

Memorado follows the GNOME project [Code of Conduct](./code-of-conduct.md). All
communications in project spaces, such as the issue tracker are expected to follow it.

