<h1 align="center">
  <img src="data/icons/hicolor/scalable/apps/io.github.fkinoshita.FlashCards.svg" alt="Flash Cards Icon" width="192" height="192"/>
  <br>
  Flash Cards
</h1>

<p align="center"><strong>Memorize anything</strong></p>

<p align="center">
  <img src="/data/screenshots/preview.png" alt="Preview"/>
  <img src="/data/screenshots/list.png" alt="Decks List"/>
  <img src="/data/screenshots/card.png" alt="Card Page"/>
</p>

Flash Cards is a simple flash cards app.

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

## CI Build (Not recommended)

If you want to quickly test FlashCards you can grab the latest CI build [here](https://nightly.link/fkinoshita/FlashCards/workflows/flatpak/main).
Then you need to unzip the archive's content and install the application with the command `flatpak install flashcards.flatpak`.

## Code of conduct

Flash Cards follows the GNOME project [Code of Conduct](./code-of-conduct.md). All
communications in project spaces, such as the issue tracker are expected to follow it.

