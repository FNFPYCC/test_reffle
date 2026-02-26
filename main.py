# main.py
# Главный файл с экранной навигацией (ScreenManager) и логикой UI:
# 1) Экран инструкций и ввода имени/возраста
# 2) Экран P1 — пульс до нагрузки (15 секунд)
# 3) Экран подтверждения приседаний (можно расширить до реального таймера)
# 4) Экран P2/P3 — пульс через 15 сек, отдых 30 сек, и снова 15 сек
# 5) Экран результата — показывает текст из ruffier.test(...)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
import buildozer

from instructions import txt_instruction, txt_test1, txt_test2, txt_test3, txt_sits
from ruffier import test
from seconds import Seconds

# Source - https://stackoverflow.com/a/47277856
# Posted by sac, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-25, License - CC BY-SA 3.0

from kivy.lang.builder import Builder

Builder.load_string('''
##kv code here
''')


#python -m PyInstaller touchtracer.spec

#buildozer

# Глобальные переменные для хранения данных между экранами.
# (Простой путь для учебного примера; в реальном проекте лучше завести модель-состояние.)
age = 7
name = ""
p1, p2, p3 = 0, 0, 0

def check_int(str_num: str):
    """Безопасный перевод строки в int. Возвращает False, если не получилось."""
    try:
        return int(str_num)
    except Exception:
        return False

class InstrScr(Screen):
    """Экран 1: Инструкция + ввод имени и возраста."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Длинный текст в ScrollView, чтобы на маленьких экранах всё пролистывалось
        instr_lbl = Label(text=txt_instruction, size_hint_y=None)
        # Чтобы Label корректно рассчитал высоту по контенту
        instr_lbl.bind(texture_size=lambda l, _: setattr(l, "height", l.texture_size[1]))
        scroll = ScrollView(size_hint=(1, 0.55))
        scroll.add_widget(instr_lbl)

        # Поле "Имя"
        lbl1 = Label(text='Введите имя:', halign='right', size_hint=(0.4, None), height='30sp')
        self.in_name = TextInput(multiline=False, size_hint=(0.6, None), height='30sp')

        # Поле "Возраст"
        lbl2 = Label(text='Введите возраст:', halign='right', size_hint=(0.4, None), height='30sp')
        self.in_age = TextInput(text='7', multiline=False, size_hint=(0.6, None), height='30sp')

        # Горизонтальные линии с меткой и полем ввода
        line1 = BoxLayout(size_hint=(0.9, None), height='34sp', spacing=8)
        line1.add_widget(lbl1)
        line1.add_widget(self.in_name)

        line2 = BoxLayout(size_hint=(0.9, None), height='34sp', spacing=8)
        line2.add_widget(lbl2)
        line2.add_widget(self.in_age)

        # Кнопка перехода к следующему экрану
        self.btn = Button(text='Начать', size_hint=(0.35, None), height='44sp', pos_hint={'center_x': 0.5})
        self.btn.on_press = self.next

        # Внешний вертикальный контейнер
        outer = BoxLayout(orientation='vertical', padding=12, spacing=10)
        outer.add_widget(scroll)
        outer.add_widget(line1)
        outer.add_widget(line2)
        outer.add_widget(self.btn)
        self.add_widget(outer)

    def next(self):
        """Сохранить имя/возраст в глобальные и перейти к экрану P1."""
        global name, age
        # .strip() убирает пробелы по краям; если пусто — оставим пустую строку (подменим позже)
        name = self.in_name.text.strip()
        age_val = check_int(self.in_age.text)
        # Минимальный возраст по методике — 7 лет
        if age_val is False or age_val < 7:
            age = 7
            self.in_age.text = str(age)  # сразу визуально исправим поле
        else:
            age = age_val
        self.manager.current = 'pulse1'

class PulseScr(Screen):
    """Экран 2: Первый замер пульса (15 секунд)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False  # флаг: можно ли уже переходить на следующий экран

        # Инструкция к шагу
        instr = Label(text=txt_test1, size_hint=(1, None))
        instr.bind(texture_size=lambda l, _: setattr(l, "height", l.texture_size[1]))

        # Таймер на 15 секунд; подпишемся на завершение, чтобы открыть ввод и кнопку
        self.lbl_sec = Seconds(15)
        self.lbl_sec.bind(done=self.sec_finished)

        # Поле ввода результата (изначально выключено)
        line = BoxLayout(size_hint=(0.9, None), height='34sp', spacing=8)
        lbl_result = Label(text='Введите результат:', halign='right', size_hint=(0.5, 1))
        self.in_result = TextInput(text='0', multiline=False, size_hint=(0.5, 1))
        self.in_result.disabled = True
        line.add_widget(lbl_result)
        line.add_widget(self.in_result)

        # Кнопка: сначала "Начать" (запускает таймер), потом станет "Продолжить"
        self.btn = Button(text='Начать', size_hint=(0.4, None), height='48sp', pos_hint={'center_x': 0.5})
        self.btn.on_press = self.next

        # Размещение элементов
        outer = BoxLayout(orientation='vertical', padding=12, spacing=10)
        outer.add_widget(instr)
        outer.add_widget(self.lbl_sec)
        outer.add_widget(line)
        outer.add_widget(self.btn)
        self.add_widget(outer)

    def sec_finished(self, *args):
        """Вызывается автоматически, когда таймер завершил 15 секунд."""
        if self.lbl_sec.done:
            self.next_screen = True
            self.in_result.disabled = False   # теперь можно вводить P1
            self.btn.disabled = False
            self.btn.text = 'Продолжить'      # режим кнопки меняется

    def next(self):
        """
        Двухрежимная кнопка:
        - Если таймер ещё не прошёл: запускаем таймер и блокируем кнопку.
        - Если уже закончили: читаем P1 и идём дальше.
        """
        if not self.next_screen:
            self.btn.disabled = True
            self.lbl_sec.start()
        else:
            global p1
            p1_val = check_int(self.in_result.text)
            if p1_val is False or p1_val <= 0:
                # Невалидный ввод: принудительно ставим 0 и просим ввести корректно
                p1 = 0
                self.in_result.text = '0'
            else:
                p1 = p1_val
                self.manager.current = 'sits'

class CheckSits(Screen):
    """Экран 3: Подтверждение выполнения приседаний (учебный упрощённый шаг)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Короткая подсказка
        instr = Label(text=txt_sits)
        # Кнопка перехода к следующему экрану
        self.btn = Button(text='Продолжить', size_hint=(0.4, None), height='48sp', pos_hint={'center_x': 0.5})
        self.btn.on_press = self.next

        outer = BoxLayout(orientation='vertical', padding=12, spacing=10)
        outer.add_widget(instr)
        outer.add_widget(self.btn)
        self.add_widget(outer)

    def next(self):
        """
        Переход на экран второго/третьего замера пульса.
        (Можно расширить экран: добавить секундомер 45 секунд и «тик-так» для темпа.)
        """
        self.manager.current = 'pulse2'

class PulseScr2(Screen):
    """Экран 4: Второй и третий замеры (15 сек, отдых 30 сек, снова 15 сек)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.stage = 0  # 0: считаем 15 сек (P2), 1: отдыхаем 30 сек, 2: считаем 15 сек (P3)

        # Инструкция к шагу
        instr = Label(text=txt_test3, size_hint=(1, None))
        instr.bind(texture_size=lambda l, _: setattr(l, "height", l.texture_size[1]))

        # Динамическая подпись над таймером
        self.lbl1 = Label(text='Считайте пульс')

        # Сам таймер (первый отрезок 15 сек)
        self.lbl_sec = Seconds(15)
        self.lbl_sec.bind(done=self.sec_finished)

        # Поле для P2 (изначально выключено, чтобы не вводили раньше времени)
        line1 = BoxLayout(size_hint=(0.9, None), height='34sp', spacing=8)
        lbl_result1 = Label(text='Результат:', halign='right', size_hint=(0.5, 1))
        self.in_result1 = TextInput(text='0', multiline=False, size_hint=(0.5, 1))
        self.in_result1.disabled = True
        line1.add_widget(lbl_result1)
        line1.add_widget(self.in_result1)

        # Поле для P3 (тоже выключено поначалу)
        line2 = BoxLayout(size_hint=(0.9, None), height='34sp', spacing=8)
        lbl_result2 = Label(text='Результат после отдыха:', halign='right', size_hint=(0.5, 1))
        self.in_result2 = TextInput(text='0', multiline=False, size_hint=(0.5, 1))
        self.in_result2.disabled = True
        line2.add_widget(lbl_result2)
        line2.add_widget(self.in_result2)

        # Кнопка "Начать" → в конце станет "Завершить"
        self.btn = Button(text='Начать', size_hint=(0.4, None), height='48sp', pos_hint={'center_x': 0.5})
        self.btn.on_press = self.next

        # Компоновка
        outer = BoxLayout(orientation='vertical', padding=12, spacing=10)
        outer.add_widget(instr)
        outer.add_widget(self.lbl1)
        outer.add_widget(self.lbl_sec)
        outer.add_widget(line1)
        outer.add_widget(line2)
        outer.add_widget(self.btn)
        self.add_widget(outer)

    def sec_finished(self, *args):
        """
        Срабатывает, когда любой из трёх отрезков времени закончился.
        По stage решаем, что делать дальше:
        - 0: открываем поле P2, запускаем отдых 30 сек
        - 1: запускаем второй 15-секундный замер
        - 2: открываем поле P3, разрешаем завершение
        """
        if not self.lbl_sec.done:
            return

        if self.stage == 0:
            # Закончили первый подсчёт (P2): разрешаем ввод и запускаем отдых
            self.stage = 1
            self.lbl1.text = 'Отдыхайте'
            self.lbl_sec.restart(30)
            self.in_result1.disabled = False

        elif self.stage == 1:
            # Закончили отдых: снова считаем пульс 15 сек (P3)
            self.stage = 2
            self.lbl1.text = 'Считайте пульс'
            self.lbl_sec.restart(15)

        elif self.stage == 2:
            # Всё: открыть поле P3, включить кнопку и сменить её текст
            self.in_result2.disabled = False
            self.btn.disabled = False
            self.btn.text = 'Завершить'
            self.next_screen = True

    def next(self):
        """
        Двухрежимная кнопка:
        - Пока стадии не пройдены: запускаем таймер и блокируем кнопку
        - Когда всё закончено: читаем P2 и P3, валидируем, идём к результату
        """
        if not self.next_screen:
            self.btn.disabled = True
            self.lbl_sec.start()
        else:
            global p2, p3
            p2_val = check_int(self.in_result1.text)
            p3_val = check_int(self.in_result2.text)

            # Простая валидация (для урока): запрещаем отрицательные и пустые значения
            if p2_val is False or p2_val < 0:
                p2 = 0
                self.in_result1.text = '0'
                return
            if p3_val is False or p3_val < 0:
                p3 = 0
                self.in_result2.text = '0'
                return

            p2, p3 = p2_val, p3_val
            self.manager.current = 'result'

class Result(Screen):
    """Экран 5: Итог — имя + интерпретация из ruffier.test()."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outer = BoxLayout(orientation='vertical', padding=12, spacing=10)
        self.instr = Label(text='')
        self.outer.add_widget(self.instr)
        self.add_widget(self.outer)

    def on_enter(self, *args):
        """
        Kivy вызывает on_enter каждый раз при показе экрана.
        Здесь формируем текст результата. Если имя пустое — подменяем на 'Участник'.
        """
        global name
        display_name = name or 'Участник'
        self.instr.text = display_name + '\n' + test(p1, p2, p3, age)

class HeartCheck(App):
    """Приложение: собираем все экраны в ScreenManager и запускаем."""
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InstrScr(name='instr'))
        sm.add_widget(PulseScr(name='pulse1'))
        sm.add_widget(CheckSits(name='sits'))
        sm.add_widget(PulseScr2(name='pulse2'))
        sm.add_widget(Result(name='result'))
        return sm

if __name__ == '__main__':
    HeartCheck().run()
