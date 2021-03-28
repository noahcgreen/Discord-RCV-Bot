class Emoji:

    CONFIRM = '✅'
    CANCEL = '❎'
    ONE = '1️⃣'
    TWO = '2️⃣'
    THREE = '3️⃣'
    FOUR = '4️⃣'
    FIVE = '5️⃣'
    SIX = '6️⃣'
    SEVEN = '7️⃣'
    EIGHT = '8️⃣'
    NINE = '9️⃣'
    TEN = '🔟'

    @staticmethod
    def statuses():
        return [Emoji.CONFIRM, Emoji.CANCEL]

    @staticmethod
    def numbers():
        return [Emoji.ONE, Emoji.TWO, Emoji.THREE, Emoji.FOUR, Emoji.FIVE,
                Emoji.SIX, Emoji.SEVEN, Emoji.EIGHT, Emoji.NINE, Emoji.TEN]
