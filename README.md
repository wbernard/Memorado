<h1 align="center">
  <img src="data/icons/hicolor/scalable/apps/im.bernard.Memorado.svg" alt="Memorado app icon" width="192" height="192"/>
  <br>
  Memorado
</h1>

<p align="center"><strong>Memorize anything</strong></p>

<p align="center">
  <img src="/data/screenshots/preview.png" alt="Preview"/>
  <img src="/data/screenshots/list.png" alt="Decks List"/>
  <img src="/data/screenshots/card.png" alt="Card Page"/>
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

## Code of conduct

Memorado follows the GNOME project [Code of Conduct](./code-of-conduct.md). All
communications in project spaces, such as the issue tracker are expected to follow it.

