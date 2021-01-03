import requests
import re
import click
import csv


class Book:
    def __init__(self, title, author, isbn, publisher, data_read):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.my_rating = ''
        self.average_rating = ''
        self.publisher = publisher
        self.binding = ''
        self.year_published = ''
        self.original_publication_year = ''
        self.data_read = data_read
        self.data_added = ''
        self.bookshelves = ''
        self.my_review = ''

    def __str__(self):
        return f"{self.title} - {self.author}. (ISBN: {self.isbn})"


def fetch_book_isbn(book_url):
    isbn = 0
    r = requests.get(f"https://www.skoob.com.br{book_url}")

    if r.status_code == 200:
        match = re.search(r'<meta property="books:isbn" content="(\w+)"', r.text)
        if match:
            isbn = match.groups()[0]
    return isbn


def export_to_csv(user, books):
    with open(f'{user}-books.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Author', 'ISBN', 'My Rating', 'Average Rating', 'Publisher', 'Binding',
                         'Year Published', 'Original Publication Year', 'Date Read', 'Date Added', 'Bookshelves',
                         'My Review'])
        for book in books:
            writer.writerow([book.title, book.author, book.isbn, book.my_rating, book.average_rating, book.publisher,
                             book.binding, book.year_published, book.original_publication_year, book.data_read,
                             book.data_added, book.bookshelves, book.my_review])


@click.command()
@click.option('-u', '--user', required=True, type=int, help='Skoob user id')
def main(user, shelf=1):
    """Skoob books exporter"""
    books = []
    page = 0
    has_next = True

    print("Reading books from Skoob...")
    while has_next:
        page += 1
        r = requests.get(f"https://www.skoob.com.br/v1/bookcase/books/{user}/shelf_id:{shelf}/page:{page}/limit:50/")

        if r.status_code == 200:
            json_response = r.json()
            books_response = json_response['response']
            has_next = json_response['paging']['next_page']
            for book_json in books_response:
                isbn = fetch_book_isbn(book_json['edicao']['url'])
                book = Book(book_json['edicao']['titulo'], book_json['edicao']['autor'].split(',')[0], isbn,
                            book_json['edicao']['editora'], book_json['dt_leitura'][:10])
                books.append(book)
                print(book)

    print("\nExporting books to csv...")
    export_to_csv(user, books)
    print("\nDone!")


if __name__ == '__main__':
    main()
