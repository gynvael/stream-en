#include <list>
#include <map>
#include <string>
#include <cstdio>
#include <cstdlib>

class Book {
 public:
  std::string name;
  long long pages;
};

std::map<int, Book> books;
std::list<Book*> favorites;
int next_idx = 1;

int get_int() {
  char line[64] = {};
  fgets(line, 63, stdin);

  int output;
  if (sscanf(line, "%i", &output) != 1) {
    puts("Protocol error!");
    exit(1);
  }

  return output;
}

long long get_ll() {
  char line[64] = {};
  fgets(line, 63, stdin);

  long long output;
  if (sscanf(line, "%lli", &output) != 1) {
    puts("Protocol error!");
    exit(1);
  }

  return output;
}

void menu(void) {
  puts("Menu:\n"
       "  1. Add a book\n"
       "  2. Delete a book\n"
       "  3. List books\n"
       "  4. Add a book to favorites\n"
       "  5. List favorites\n"
       "  0. Quit");
}

void add_book() {
  char buffer[1024];

  puts("-- Adding book!");
  printf("Name: ");

  fgets(buffer, 1023, stdin);
  sscanf(buffer, "%1023[^\n]", buffer);

  printf("Pages: ");
  long long pages = get_ll();

  books[next_idx] = Book{ buffer, pages };

  printf("Added as %i\n", next_idx++);
}

void delete_book() {

  puts("-- Delete book!");

  printf("Which book? ");

  int book_id = get_int();

  if (books.find(book_id) != books.end()) {
    books.erase(book_id);
    puts("Removed.");
  } else {
    puts("Protocol error!");
    exit(1);
  }
}

void list_books() {
  puts("-- Listing books!");
  for (const auto& book : books) {
    printf("%i. %s (%lli)\n",
      book.first,
      book.second.name.c_str(),
      book.second.pages);
  }
}

void add_fav() {
  puts("-- Adding fav!");

  printf("Which book? ");
  int book_id = get_int();

  if (books.find(book_id) != books.end()) {
    favorites.push_back(&books[book_id]);
    puts("Added to favorites");
  } else {
    puts("Protocol error!");
    exit(1);
  }
}

void list_fav() {
  puts("-- Listing favs!");
  for (Book *book : favorites) {
    printf("%s (%lli)\n",
      book->name.c_str(),
      book->pages);
  }
}

int main(void) {
  setbuf(stdout, NULL);
  //setlinebuf(stdin);
  puts("Welcome to the library");

  for (;;) {
    menu();
    printf("Choice? ");

    int choice = get_int();

    switch (choice) {
      case 1: add_book(); break;
      case 2: delete_book(); break;
      case 3: list_books(); break;
      case 4: add_fav(); break;
      case 5: list_fav(); break;

      case 0: puts("Bye!"); return 0;

      default:
        puts("Yeah, right. Well, try again.");
        continue;
    }
  }

  return 0;
}
