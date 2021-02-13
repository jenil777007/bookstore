class Book:
    def __init__(self, id, title, thumbnail, quantity, link):
        self.id = id
        self.title = title
        self.thumbnail = thumbnail
        self.quantity = quantity
        self.link = link

    def to_dict(self):
        dest = {
            "id": self.id,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "quantity": self.quantity,
            "link": self.link,
        }
        return dest

    def __str__(self):
        return f"id -> {self.id}, title -> {self.title}, thumbnail -> {self.thumbnail}, quantity -> {self.quantity}, link -> {self.link}"