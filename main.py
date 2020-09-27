# Был не понятен один момент в ТЗ: нужно ли считать, что продукты,
# к которым по условию оставлены отзывы были куплены и магазин получл приыль?
# Я это не учитывал, то есть прибыль приносят непосредственно сформерованные заказы, но на логику работы это ни как не повлияет,
# разве что в 3 пункте выручка по категории "техника" будет равняться нулю
import datetime
from copy import deepcopy


def formDeliveryDate(day, month, year, deferred_days=0):
    # Для работы с датой я использую модуль datetime, а это вспомогательная функция, для удобства
    date = datetime.date.today()
    if day != 0 and month != 0 and year != 0:
        date = datetime.date(year, month, day)
    return date + datetime.timedelta(days=deferred_days)


def getProfit(period=None, category=None):
    # Возвращает выручку магазина за определенное время (по товару определенной категории, если она задана),
    # если period не задан, то возвращает выручку за текущий день
    profit = 0
    if period is None:
        for order in Order.order_list:
            if order.order_date == datetime.date.today() and (category in order.product.categories or category is None):
                profit += order.product.price
        if category is None:
            print("[ВЫРУЧКА]:", "Выручка за сегодняшний день составила", profit)
        else:
            print("[ВЫРУЧКА]:", " Выручка за сегодняшний день в категории \"", category, "\" составила ", profit,
                  sep="")
    if period == "year":
        # Выручка за последние 365 дней
        date = datetime.date.today()
        date -= datetime.timedelta(days=365)
        for order in Order.order_list:
            if date <= order.order_date <= datetime.date.today() and (
                    category in order.product.categories or category is None):
                profit += order.product.price
        if category is None:
            print("[ВЫРУЧКА]:", "Выручка за последний год составила", profit)
        else:
            print("[ВЫРУЧКА]:", " Выручка за последний год в категории \"", category, "\" составила ", profit, sep="")
    return profit


def printProductList():
    # Выводит список продуктов вместе с их ценой
    print("=" * 10, "в нашем магазине вы можете купить", "=" * 10)
    for product in Product.products_list.values():
        print(product.name, "по цене", round(product.price, 2))
    print("=" * 55)


def printProductMeanRating(product_name=""):
    # Выводит среднюю оценку товара. Если product_name не задан, то выводит средние оценки всех товаров
    if product_name != "":
        Product.products_list[product_name].getMeanRating()
        return
    for product in Product.products_list.values():
        product.getMeanRating()


def printBadReviewsDetails(category):
    for product in Product.products_list.values():
        if category not in product.categories:
            continue
        for product_review in product.reviews:
            if product_review.rating <= 3:
                print("Пользователь с e-mail'ом ", product_review.user.email, " оставил плохой отзыв на товар ",
                      product.name, sep="")


def announceSale(category, discount):
    # Объявляет скидку на товары определенной категории, 0 <= discount <= 100
    # Скидка остается навсегда, то есть эта функция меняет стоимость товаров определенной категории
    for product in Product.products_list.values():
        if category in product.categories:
            product.price = product.price * (1 - discount / 100)
    print("[АКЦИЯ]:", "На все товары категории", category.upper(), "скидка", discount, "процентов!")


class User:

    def __init__(self, login, email, delivery_address):
        self.login = login
        self.email = email
        self.delivery_address = delivery_address

    def rateProduct(self, product, rating):
        product.addRating(rating, self)

    def formOrder(self, product, delivery_date):
        order = Order(product, self, datetime.date.today(), delivery_date)
        order.makeOrder()


class Review:

    def __init__(self, rating, user):
        self.rating = rating
        self.user = user


class Product:
    # Я использую именно словарь, потому что так удобнее обрщаться к элементам, в качестве ключа выступает наименование товара
    products_list = {}

    def __init__(self, name, price, *categories, reviews=[]):
        self.price = price
        self.name = name
        self.reviews = []
        for review in reviews:
            self.reviews.append(review)
        self.categories = []
        for category in categories:
            self.categories.append(category)
        Product.products_list[name] = self

    def calculateRating(self):
        if len(self.reviews) == 0:
            return 0
        sum_of_rating = [i.rating for i in self.reviews]
        return round(sum(sum_of_rating) / len(sum_of_rating), 2)

    def getMeanRating(self):
        rating = self.calculateRating()
        print("[ТОВАР]: Рейтинг товара \"", self.name, "\"", " равен ", rating, sep="")
        return rating

    def addRating(self, rating, user):
        self.reviews.append(Review(rating, user))


class Order:
    # Список заказов нужен для того, чтобы считать выручку за определенный период
    order_list = []

    def __init__(self, product, user, order_date, delivery_date):
        # Я использую deepcopy, чтобы в order_list сохранялись данные продукта на момент заказа(т.к цена может измениться из-за акции)
        self.product = deepcopy(product)
        self.user = user
        self.order_date = order_date
        self.delivery_date = delivery_date

    def makeOrder(self):
        if self.order_date > self.delivery_date:
            print("[ОШИБКА]:", "Ошибка! В заказе", self.user.login, self.order_date,
                  "\n\t\t\tДата доставки не может быть раньше даты заказа!")
        else:
            print("[ЗАКАЗ]:", self.user.login, "заказал", self.product.name, "по цене", self.product.price
                  , "\n\t\t\tЗаказ будет доставлен", self.delivery_date)
            # проверка того, что подсчет выручки за год работает правильно:
            # искусственно добавляем заказ от Пети, который сделан раньше, чем сегодня
            # if self.user.login == "PetrIvanovich":
            # self.order_date = datetime.date.today() - datetime.timedelta(days = 100)
            Order.order_list.append(self)


# Подготовка
vasya = User("vas'ok", "vasyan228@mail.ru", "botanicheskaya 64k3")
petya = User("PetrIvanovich", "petrusha@mail.ru", "botanicheskaya 70k4")
drel = Product("дрель", 999, "техника", "товары для дома", reviews=[Review(5, petya)])
bruki = Product("брюки мужские", 699, "одежда", "мужская одежда", reviews=[Review(3, vasya)])
palto = Product("пальто женское", 7000, "одежда", "женская одежда", reviews=[Review(5, vasya), Review(1, petya)])
printProductList()

# Пункт 1
petya.formOrder(bruki, formDeliveryDate(1, 10, 2020))
vasya.formOrder(drel, formDeliveryDate(1, 9, 2020))
petya.rateProduct(bruki, 5)

# Пункт 2
announceSale("одежда", 30)
petya.formOrder(palto, formDeliveryDate(0, 0, 0, deferred_days=14))
vasya.formOrder(palto, formDeliveryDate(0, 0, 0, deferred_days=14))
getProfit()

# Пункт 3
printProductMeanRating()
printProductMeanRating(product_name="брюки мужские")
printBadReviewsDetails("техника")  # ничего не выводит, т.к на технику не было плохих отзывов
getProfit(period="year", category="техника")
