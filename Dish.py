import flet as ft


class Ingredient:
    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name


class Aliment(Ingredient):

    def __init__(self, name: str, proportion: float, price_per_kilo: float):
        self.name = name
        self.proportion = proportion
        self.price_per_kilo = price_per_kilo
        self.price = 0
        self.check_price()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}({self.proportion}g) = {format(self.price, '.2f')}€"

    def __add__(self, other):
        if self.name == other.name:
            return Aliment(self.name, self.proportion + other.proportion, self.price_per_kilo)

    def check_price(self):
        self.price = (self.proportion / 1000) * self.price_per_kilo


class Liquid(Ingredient):

    def __init__(self, name: str, volume: int, price_per_liter: float):
        self.name = name
        self.volume = volume
        self.price_per_liter = price_per_liter
        self.price = 0
        self.check_price()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}({self.volume}mL) = {format(self.price, '.2f')}€"

    def check_price(self):
        self.price = (self.volume / 1000) * self.price_per_liter

    def __add__(self, other):
        if self.name == other.name:
            return Liquid(self.name, self.volume + other.nb_of_piece, self.price_per_liter)


class Piece(Ingredient):

    def __init__(self, name: str, nb_of_piece: int, price_per_packet: float, number_of_piece_by_packet: float):
        self.name = name
        self.nb_of_piece = nb_of_piece
        self.price_per_packet = price_per_packet
        self.number_of_piece_by_packet = number_of_piece_by_packet
        self.price = 0
        self.check_price()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.name}({self.nb_of_piece}) = {format(self.price, '.2f')}€"

    def check_price(self):
        self.price = (self.nb_of_piece / self.number_of_piece_by_packet) * self.price_per_packet

    def __add__(self, other):
        if self.name == other.name:
            return Piece(self.name, self.nb_of_piece + other.nb_of_piece, self.price_per_packet,
                         self.number_of_piece_by_packet)


class Dish:
    dishes = {}

    def __init__(self, name: str):
        self.name = name
        self.parts = []
        self.cost = 0
        Dish.dishes[self.name] = self

    def __str__(self):
        return self.get_markdown()

    def get_markdown(self) -> str:
        return f"{self.name}({format(self.cost, '.2f')}€)"

    def check_cost(self):
        self.cost = sum([part.price for part in self.parts])

    def add_part(self, part: Aliment | Liquid):
        if part in self.parts:
            self.parts[self.parts.index(part)] += part
        else:
            self.parts.append(part)
        self.check_cost()

    def remove_part(self):
        print(self.parts)
        self.parts.pop(int(input("Quel aliment voulez-vous enlever ? ")))

    def to_flet_dish_selector(self, on_click=None):
        res = ft.Card(
            content=ft.Container(
                content=ft.Column(controls=[ft.Text(f"{self} :", style=ft.TextThemeStyle.BODY_LARGE)],
                                  scroll=ft.ScrollMode.AUTO),
                data=self,
                on_click=on_click,
                padding=15
            )
        )

        dish_parts = ft.Column(height=200, scroll=ft.ScrollMode.AUTO)

        for part in self.parts:
            dish_parts.controls.append(ft.Text(value=" - [ ] " + str(part)))

        res.content.content.controls.append(dish_parts)
        return res

    def to_flet_dish_selected(self):
        return ft.Container(content=ft.Column(controls=[ft.Checkbox(label=str(self), value=True)]),
                            border=ft.border.all(2))


Dish("Pâtes carbonara")
Dish.dishes["Pâtes carbonara"].add_part(Aliment("Spaghetti", 150, 2.75))
Dish.dishes["Pâtes carbonara"].add_part(Aliment("Lardons", 100, 19.9))
Dish.dishes["Pâtes carbonara"].add_part(Liquid("Crème fraîche", 100, 5))

Dish("Pizza")
Dish.dishes["Pizza"].add_part(Liquid("Sauce tomate", 125, 1.50))
Dish.dishes["Pizza"].add_part(Aliment("Tomates", 100, 3))
Dish.dishes["Pizza"].add_part(Aliment("Levure chimique", 5, 23.33))
Dish.dishes["Pizza"].add_part(Aliment("Farine", 120, 0.74))

for name in range(100):
    Dish(str(name))
    for aliment in range(5):
        Dish.dishes[str(name)].add_part(Aliment(str(aliment), 10, 10))
