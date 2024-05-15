import datetime, sys, os
from functools import wraps
from Dish import *

from strings import STRINGS

print(f"Platform detected : {sys.platform}")
if sys.platform == 'linux':
    brain_path = "/home/maxime/Documents/GitHub/2nd-Brain/"
elif sys.platform == 'win32':
    brain_path = "D:/Mon drive/2nd-Brain/"
else:
    brain_path = "./"

SIZE_MIN = 85

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def main(page: ft.Page):
    page.window_maximized = True
    page.spacing = 0
    page.language = open("params.txt", 'r', encoding='utf-8').read()
    page.mode = "select_dish"
    page.theme = ft.Theme(color_scheme_seed="green")
    page.theme_mode = ft.ThemeMode.LIGHT
    dialog_material = ft.AlertDialog(title=ft.Text(""), actions_alignment=ft.MainAxisAlignment.END)
    page.dialog = dialog_material

    # ***
    def toggle_theme_mode(e):
        if page.theme_mode == ft.ThemeMode.DARK :
            page.theme_mode = ft.ThemeMode.LIGHT
            e.control.label = "Light theme"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            e.control.label = "Dark theme"
        page.update()

    def restart(e):
        page.window_close()
        restart_script()

    def close_dialog(e):
        dialog_material.open = False
        print(dialog_material.open)

    def dialog(text: str, is_error: bool = False, actions=[]):
        dialog_material.title.value = text
        if actions == []:
            dialog_material.actions = [ft.TextButton("Ok", on_click=close_dialog)]
        else:
            dialog_material.actions = actions
        if is_error:
            dialog_material.title.color = ft.colors.RED
        dialog_material.open = True
        page.update()

    def refresh_header_size():
        a_tenth = 0.1 * page.window_height
        if a_tenth > SIZE_MIN:
            header.height = 0.1 * page.window_height
        else:
            header.height = 75

    def refresh_body_size():
        a_tenth = 0.1 * page.window_height
        if a_tenth > SIZE_MIN:
            body.height = 0.8 * page.window_height
        else:
            body.height = page.window_height - (SIZE_MIN * 2)

    def refresh_footer_size():
        a_tenth = 0.1 * page.window_height
        if a_tenth > SIZE_MIN:
            footer.height = 0.1 * page.window_height
        else:
            footer.height = SIZE_MIN

    def refresh_controls_size():
        dishes_list.width = page.window_width - 300
        R_dishes_selector.width = page.window_width
        R_dishes_selector.height = body.height - 25

    def on_resize(e):
        refresh_header_size()
        refresh_body_size()
        refresh_footer_size()
        refresh_controls_size()
        page.update()

    page.on_resize = on_resize

    def clear_after(func):
        wraps(func)

        def wrapper(*args, **kwargs):
            ancient_controls = body.controls[:]  # sauvegarde les boîtes du body d'avant
            body.controls.clear()  # vide les controls du body
            val = func(*args, **kwargs)  # lance la fonction
            body.controls.clear()  # revide le body
            body.controls = ancient_controls  # remet ce qu'il y avait avant dans le body
            page.update()  # actualise l'écran
            if val:
                return val

        return wrapper

    def set_language(e):
        language = e.control.content.controls[1].data
        if page.language != language:
            open("params.txt", 'w', encoding='utf-8').write(language.lower())
            dialog(STRINGS[language.lower()]["restart_app"],
                   actions=[ft.TextButton("Restart later", on_click=close_dialog),
                            ft.TextButton("Restart now", on_click=restart)])

    def update_C_selected_dishes():
        dishes_without_multiples = list(set(selected_dishes))
        controls = []

        for dish in dishes_without_multiples:
            nb_dish = selected_dishes.count(dish)
            total_dishes_price = sum([dish_.cost for dish_ in selected_dishes if dish_ == dish])

            container = ft.Container(data=dish, border=ft.border.only(left=ft.border.BorderSide(2)))
            icon_less_one = ft.IconButton(icon=ft.icons.EXPOSURE_MINUS_1_ROUNDED,
                                          tooltip=STRINGS[page.language]["remove_elt"],
                                          on_click=deselect_dish, data=dish)
            T_text = ft.Text(f"{dish}({nb_dish}) = {format(total_dishes_price, '.2f')}€",
                             width=C_selected_dishes.width - 100, height=container.height)
            icon_less_all = ft.IconButton(icon=ft.icons.CLOSE_ROUNDED,
                                          tooltip=STRINGS[page.language]["remove_entirely_elt"],
                                          on_click=deselect_entirely_dish, data=dish)
            container.content = ft.Row(controls=[icon_less_one, T_text, icon_less_all], spacing=0)
            container.tooltip = T_text.value
            controls.append(container)

        C_selected_dishes.controls = controls

    def click_on_dish(e: ft.ControlEvent):
        container = e.control
        dish = container.data
        if page.mode == "select_dish":
            selected_dishes.append(dish)
        elif page.mode == "remove_dish":
            deselect_entirely_dish(e)
            dishes_list.controls.remove(container)
            Dish.dishes.pop(dish.name)
            page.mode = "select_dish"
            for dish in dishes_list.controls:
                dish.on_hover = None
            BTN_add_dish.visible = True
            BTN_remove_dish.visible = True
            body_title.value = "Dishes list"
            BTN_cancel_remove.visible = False

        update_total(e)
        update_C_selected_dishes()
        page.update()

    def deselect_dish(e):
        dish = e.control.data
        selected_dishes.remove(dish)
        update_total(e)
        update_C_selected_dishes()
        page.update()

    def deselect_entirely_dish(e):
        dish = e.control.data
        while dish in selected_dishes:
            selected_dishes.remove(dish)
        update_total(e)
        update_C_selected_dishes()
        page.update()

    def convert_all_dishes_to_flet():
        res = ft.GridView(child_aspect_ratio=1.0, spacing=5, max_extent=250, width=page.window_width - 300, padding=10)
        for dish in Dish.dishes.values():
            res.controls.append(dish.to_flet_dish_selector(click_on_dish))
        return res

    def update_all_prices():
        all_prices.clear()
        all_prices.extend([dish.cost for dish in selected_dishes])

    def update_total(e: ft.ControlEvent = 0):
        update_all_prices()
        total.value = f"{format(sum(all_prices), '.2f')}€"
        update_total_color()

    def update_total_color():
        if sum(all_prices) == 0.0:
            if page.theme_mode == ft.ThemeMode.LIGHT:
                total.color = ft.colors.BLACK
            else:
                total.color = ft.colors.WHITE
        elif float(sum(all_prices)) > (float(budget_cap.value) if budget_cap.value != '' else 0):
            total.color = ft.colors.RED
        else:
            total.color = ft.colors.GREEN
        page.update()

    def write_to_cursor(src: str, text_to_write: str, cursor_index: int) -> str:
        cursor_text = f"<% tp.file.cursor({cursor_index}) %>"
        if src.count(cursor_text) == 1:
            sides = src.split(cursor_text)
            return sides[0] + text_to_write + sides[1]
        else:
            raise Exception(f"More than 1 cursor {cursor_index} or no cursor {cursor_index} at all")

    def to_md(e):
        if selected_dishes != []:
            text = get_markdown_text()
            open(brain_path + f"5. À Trier/Shopping_list_{datetime.date.today()}.md", 'w',
                 encoding="utf-8").write(text)
        else:
            dialog(STRINGS[page.language]["no_dish"], True)

    def get_markdown_text() -> str:
        shopping_list_text = next_meals() + '\n' + ingredients_list_md() + '\n' + total_md()

        note_template = open(brain_path + "0. Datas/Modèles/New note.md", 'r', encoding='utf-8').read()
        note_with_source = write_to_cursor(note_template, STRINGS[page.language]["header_title"], 0)
        note_with_shopping_list = write_to_cursor(note_with_source, shopping_list_text, 1)

        return note_with_shopping_list

    def total_md() -> str:
        return total.value

    def get_ingredients_list():
        all_ingredients = []
        for dish in selected_dishes:
            for part in dish.parts:
                if part in all_ingredients:
                    all_ingredients[all_ingredients.index(part)] += part
                else:
                    all_ingredients.append(part)
        return sorted(all_ingredients)

    def ingredients_list_md():
        result = STRINGS[page.language]["ingredients"] + ':\n'
        for ingredient in get_ingredients_list():
            result += '- [ ] ' + str(ingredient) + '\n'
        return result

    def next_meals() -> str:
        selected_dishes_name = [dish.name for dish in sorted(selected_dishes)]
        result = STRINGS[page.language]["next_meals"] + '\n'
        for dish in selected_dishes_name:
            result += '- ' + dish + '\n'
        return result

    @clear_after
    def add_dish(e):
        """
        FINISHED
        """

        def submit(e):
            dish["name"] = FIELD_dish_name.value
            if not dish_name_valid():
                dialog(STRINGS[page.language]["ERR_dish_name"])
                BTN_submit.data = False
                pass
            elif dish["parts"] == []:
                dialog(STRINGS[page.language]["ERR_dish_ingredients"])
                BTN_submit.data = False
                pass
            else:
                dish_added = Dish(dish["name"])
                for part in dish["parts"]:
                    dish_added.add_part(part)
                dishes_list.controls.append(dish_added.to_flet_dish_selector(click_on_dish))
                BTN_submit.data = True
                page.update()

        def cancel(e):
            BTN_submit.data = True
            page.update()

        def dish_name_valid():
            return dish["name"] != "" and FIELD_dish_name.error_text == ""

        def add_part(e):
            if datas_valid():
                dish["name"] = FIELD_dish_name.value
                if DD_unity.value == "mL":
                    part = Liquid(FIELD_part_name.value, int(FIELD_proportion.value), float(FIELD_part_price.value))
                elif DD_unity.value == "g":
                    part = Aliment(FIELD_part_name.value, int(FIELD_proportion.value), float(FIELD_part_price.value))
                elif DD_unity.value == STRINGS[page.language]["item"]:
                    part = Piece(FIELD_part_name.value, int(FIELD_proportion.value), float(FIELD_part_price.value),
                                 float(FIELD_nb_per_packet.value))
                dish["parts"].append(part)
                dish_parts.controls.append(ft.Text(value=" - [ ] " + str(part)))
                update_dish_title()

                clear_inputs()
            else:
                dialog(STRINGS[page.language]["ERR_ingredients_infos"], True)

        def datas_valid():
            return FIELD_part_name.value != "" and FIELD_proportion.value != "0" and FIELD_part_price.value != "0"

        def clear_inputs():
            FIELD_part_name.value = ""
            FIELD_proportion.value = "0"
            FIELD_part_price.value = "0"
            FIELD_nb_per_packet.value = "0"

        def check_FIELD_dish_name(e):
            if FIELD_dish_name.value in Dish.dishes.keys():
                FIELD_dish_name.error_text = STRINGS[page.language]["ERR_dish_exists"]
            else:
                FIELD_dish_name.error_text = ""
            update_dish_title()

        def update_dish_title():
            dish_title.value = f"{FIELD_dish_name.value}({format(sum([part.price for part in dish['parts']]), '.2f')}€) :"

        def check_FIELD_proportion(e):
            if not is_valid(FIELD_proportion.value):
                FIELD_proportion.error_text = STRINGS[page.language]["ERR_nb_invalid"]
            else:
                FIELD_proportion.error_text = ""

        def check_FIELD_part_price(e):
            if not is_valid(FIELD_proportion.value):
                FIELD_part_price.error_text = STRINGS[page.language]["ERR_nb_invalid"]
            else:
                FIELD_part_price.error_text = ""

        def check_FIELD_nb_per_packet(e):
            if not is_valid(FIELD_nb_per_packet.value):
                FIELD_nb_per_packet.error_text = STRINGS[page.language]["ERR_nb_invalid"]
            else:
                FIELD_nb_per_packet.error_text = ""

        def is_valid(text: str):
            try:
                float(text)
            except ValueError:
                return False
            else:
                return True

        def check_DD_unity(e):
            if DD_unity.value == "g":
                FIELD_part_price.label = STRINGS[page.language]["price_kg"]
                FIELD_proportion.label = STRINGS[page.language]["kg_needed"]
                FIELD_nb_per_packet.visible = False
            elif DD_unity.value == "mL":
                FIELD_part_price.label = STRINGS[page.language]["price_l"]
                FIELD_proportion.label = STRINGS[page.language]["l_needed"]
                FIELD_nb_per_packet.visible = False
            elif DD_unity.value == "unité":
                FIELD_part_price.label = STRINGS[page.language]["item_price"]
                FIELD_proportion.label = STRINGS[page.language]["item_needed"]
                FIELD_nb_per_packet.visible = True
            FIELD_proportion.suffix_text = DD_unity.value

        dish = {"name": "", "parts": []}

        title = ft.Text(STRINGS[page.language]["add_dish"], style=ft.TextThemeStyle.HEADLINE_MEDIUM)
        BTN_cancel = ft.FilledButton(STRINGS[page.language]["cancel"], on_click=cancel)
        body.controls.append(ft.Row(controls=[title, BTN_cancel]))

        ROW_dish_creator = ft.Row(width=page.window_width, height=body.height - 25, scroll=ft.ScrollMode.AUTO)

        C_dish_parameters = ft.Column(width=0.7 * page.window_width)
        FIELD_dish_name = ft.TextField(label=STRINGS[page.language]["dish_name"], on_change=check_FIELD_dish_name,
                                       error_text="")
        C_dish_parameters.controls.append(FIELD_dish_name)
        C_dish_parameters.controls.append(
            ft.Text(STRINGS[page.language]["ingredients"], style=ft.TextThemeStyle.HEADLINE_SMALL))
        FIELD_part_name = ft.TextField(label=STRINGS[page.language]["ingredient_name"])
        DD_unity = ft.Dropdown(options=[ft.dropdown.Option("mL"), ft.dropdown.Option("g"), ft.dropdown.Option("unité")],
                               width=100, value="g",
                               on_change=check_DD_unity)
        FIELD_proportion = ft.TextField(label=STRINGS[page.language]["kg_needed"],
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        value="0",
                                        on_change=check_FIELD_proportion,
                                        suffix_text=DD_unity.value)
        FIELD_part_price = ft.TextField(label=STRINGS[page.language]["price_kg"],
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        value="0",
                                        suffix_text="€",
                                        on_change=check_FIELD_part_price)
        FIELD_nb_per_packet = ft.TextField(label=STRINGS[page.language]["items_per_packet"], value="0",
                                           on_change=check_FIELD_nb_per_packet,
                                           width=200,
                                           visible=False)
        ROW_proportion = ft.Row(controls=[FIELD_proportion, DD_unity, FIELD_nb_per_packet, FIELD_part_price],
                                width=C_dish_parameters.width - 10)
        BTN_add_part = ft.FilledButton(STRINGS[page.language]["add_ingredient"], icon=ft.icons.ADD_ROUNDED,
                                       on_click=add_part)
        C_dish_parameters.controls.extend([FIELD_part_name, ROW_proportion, BTN_add_part])
        BTN_submit = ft.FilledButton(STRINGS[page.language]["submit"], on_click=submit, data=False)

        C_dish_print = ft.Column(width=0.3 * page.window_width)
        dish_title = ft.Text(dish["name"], style=ft.TextThemeStyle.BODY_LARGE)
        dish_parts = ft.Column(height=200, scroll=ft.ScrollMode.AUTO)
        dish_print = ft.Container(content=ft.Column(controls=[dish_title, dish_parts]), border=ft.border.all(2),
                                  border_radius=ft.border_radius.all(5), width=250)
        C_dish_print.controls.extend([dish_print, BTN_submit])

        ROW_dish_creator.controls.extend([C_dish_parameters, C_dish_print])

        body.controls.append(ROW_dish_creator)

        while BTN_submit.data == False:
            page.update()

    def animate(e):
        container = e.control
        container.border = ft.border.all(2, "red") if e.data == "true" else ft.border.all(2, "black")
        page.update()

    def remove_dish(e):
        for dish in dishes_list.controls:
            dish.on_hover = animate
        page.mode = "remove_dish"
        BTN_add_dish.visible = False
        BTN_remove_dish.visible = False
        BTN_cancel_remove.visible = True
        body_title.value = STRINGS[page.language]["remove_dish_title"]

        page.update()

    def cancel_remove(e):
        page.mode = "select_dish"
        for dish in dishes_list.controls:
            dish.on_hover = None
        BTN_add_dish.visible = True
        BTN_remove_dish.visible = True
        body_title.value = STRINGS[page.language]["dishes_list"]
        BTN_cancel_remove.visible = False
        update_total(e)
        update_C_selected_dishes()
        page.update()

    # ***
    header = ft.Row(controls=[ft.Text(STRINGS[page.language]["header_title"], style=ft.TextThemeStyle.HEADLINE_LARGE)],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=0.1 * page.window_height,
                    spacing=10)
    budget_cap = ft.TextField(label=STRINGS[page.language]["budget_cap"], value="25", on_change=update_total)
    BTN_toggle_theme_mode = ft.Switch(label="Light theme", on_change=toggle_theme_mode)
    header.controls.insert(0, budget_cap)
    header.controls.append(BTN_toggle_theme_mode)
    languages = {"english": ft.Row(controls=[ft.Image("english_flag.ico", width=20, height=20, fit=ft.ImageFit.FILL),
                                             ft.Text("English", data="english")]),
                 "french": ft.Row(controls=[ft.Image("french_flag.ico", width=20, height=20, fit=ft.ImageFit.FILL),
                                            ft.Text("Français", data="french")])}
    language_selector = ft.PopupMenuButton(
        items=[ft.PopupMenuItem(content=languages[language], on_click=set_language) for language in languages.keys()])
    header.controls.append(language_selector)

    # ***
    body = ft.Column(height=0.8 * page.window_height, spacing=10)
    body_title = ft.Text(STRINGS[page.language]["dishes_list"], style=ft.TextThemeStyle.HEADLINE_MEDIUM)
    BTN_add_dish = ft.FilledButton(STRINGS[page.language]["add_dish"], icon=ft.icons.ADD_ROUNDED, on_click=add_dish)
    BTN_remove_dish = ft.FilledButton(STRINGS[page.language]["remove_dish"], icon=ft.icons.CLOSE_ROUNDED,
                                      on_click=remove_dish)
    BTN_cancel_remove = ft.FilledButton(STRINGS[page.language]["cancel"], icon=ft.icons.CLOSE_ROUNDED,
                                        on_click=cancel_remove, visible=False)
    body.controls.append(ft.Row(controls=[body_title, BTN_add_dish, BTN_remove_dish, BTN_cancel_remove]))

    selected_dishes = []
    C_selected_dishes = ft.Column(width=300, scroll=ft.ScrollMode.AUTO)
    R_dishes_selector = ft.Row(width=page.window_width, height=body.height - 25, scroll=ft.ScrollMode.AUTO)
    dishes_list = convert_all_dishes_to_flet()
    R_dishes_selector.controls.extend([dishes_list, C_selected_dishes])
    body.controls.append(R_dishes_selector)

    # ***
    footer = ft.Row(alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    height=0.1 * page.window_height,
                    spacing=10)
    all_prices = []
    total = ft.Text(f"{format(sum(all_prices), '.2f')}€", style=ft.TextThemeStyle.HEADLINE_SMALL)
    footer.controls.extend(
        [ft.Text(STRINGS[page.language]["total"] + ': ', style=ft.TextThemeStyle.HEADLINE_SMALL), total])
    to_md_btn = ft.FilledButton(STRINGS[page.language]["export"], icon=ft.icons.ARROW_FORWARD, on_click=to_md)
    footer.controls.append(to_md_btn)

    page.add(ft.Container(content=header))
    page.add(ft.Container(content=body))
    page.add(ft.Container(content=footer))


# from flet_icon import Application

ft.app(target=main)
# ft.app(target=Application())
