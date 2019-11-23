# SharePDF

SharePDF is a PDF-Viewer build to view and edit PDFs collaboratively.

## Requirements

- Python v3.7
- [PyQt5](https://pypi.org/project/PyQt5/)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/)
- [Pickle](https://docs.python.org/2/library/pickle.html)

To set up the Libraries use the following (preferably in a virtual environment using venv)

```shell
pip install PyQt5 PyMuPDF
```

## Features

### Features (finished)

### Features (being worked on)

- View PDFs with all the features of a standart PDF-viewer

### Features (planed)

- PDF editing features
- View Cursors of other users (with different colors)
    - display username next to cursor
- View Comments of other users (with different colors)
- Be able to draw on the PDF (also with different colors)

# Structure

## Server

- Lobbyconnector/creator class
    - Dictionary with IP-Adress as key and a tupel with user-name and lobby as value
    
### Protocol

Send Python classes serialized (Pickel) (via TCP):
 - plaintext txt
 - PDF pdf
 - Lobby lby
 - StatusServer sti (send via UDP)
    - dictionary (key: Username) with StatusClient classes (or None if there is no change in status)
    - list with connected/disconnected events
 - StatusClient sto (send via UDP)
    - y scroll value
    - mouse position
    - list with marker objects (marked text, comments, etc.)

## Client

- Connectionhandler class