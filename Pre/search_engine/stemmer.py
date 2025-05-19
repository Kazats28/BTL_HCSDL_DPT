
import re

class PorterStemmer:
    def __init__(self):
        self.vowels = "aeiou"

    def is_consonant(self, word, i):
        if i < 0 or i >= len(word):
            return False
        if word[i] in self.vowels:
            return False
        if word[i] == 'y':
            if i == 0:
                return True
            else:
                return not self.is_consonant(word, i - 1)
        return True

    def measure(self, word):
        m = 0
        i = 0
        length = len(word)
        while i < length:
            while i < length and self.is_consonant(word, i):
                i += 1
            if i < length:
                i += 1
            else:
                break
            while i < length and not self.is_consonant(word, i):
                i += 1
            if i < length:
                m += 1
        return m

    def contains_vowel(self, word):
        return any(not self.is_consonant(word, i) for i in range(len(word)))

    def ends_double_consonant(self, word):
        return len(word) >= 2 and word[-1] == word[-2] and self.is_consonant(word, len(word) - 1)

    def cvc(self, word):
        if len(word) >= 3 and self.is_consonant(word, -1) and not self.is_consonant(word, -2) and self.is_consonant(word, -3):
            if word[-1] not in "wxy":
                return True
        return False

    def step1a(self, word):
        if word.endswith("sses"):
            return word[:-2]
        elif word.endswith("ies"):
            return word[:-2]
        elif word.endswith("ss"):
            return word
        elif word.endswith("s"):
            return word[:-1]
        return word

    def step1b(self, word):
        if word.endswith("eed"):
            stem = word[:-3]
            if self.measure(stem) > 0:
                return stem + "ee"
            else:
                return word
        elif word.endswith("ed"):
            stem = word[:-2]
            if self.contains_vowel(stem):
                word = stem
                word = self.step1b_helper(word)
        elif word.endswith("ing"):
            stem = word[:-3]
            if self.contains_vowel(stem):
                word = stem
                word = self.step1b_helper(word)
        return word

    def step1b_helper(self, word):
        if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
            return word + "e"
        elif self.ends_double_consonant(word):
            if word[-1] not in "lsz":
                return word[:-1]
        elif self.measure(word) == 1 and self.cvc(word):
            return word + "e"
        return word

    def step1c(self, word):
        if word.endswith("y") and self.contains_vowel(word[:-1]):
            return word[:-1] + "i"
        return word

    def step2(self, word):
        suffixes = {
            "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
            "izer": "ize", "abli": "able", "alli": "al", "entli": "ent",
            "eli": "e", "ousli": "ous", "ization": "ize", "ation": "ate",
            "ator": "ate", "alism": "al", "iveness": "ive", "fulness": "ful",
            "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble"
        }
        for key in suffixes:
            if word.endswith(key):
                stem = word[:-len(key)]
                if self.measure(stem) > 0:
                    return stem + suffixes[key]
        return word

    def step3(self, word):
        suffixes = {
            "icate": "ic", "ative": "", "alize": "al", "iciti": "ic",
            "ical": "ic", "ful": "", "ness": ""
        }
        for key in suffixes:
            if word.endswith(key):
                stem = word[:-len(key)]
                if self.measure(stem) > 0:
                    return stem + suffixes[key]
        return word

    def step4(self, word):
        suffixes = [
            "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
            "ment", "ent", "ion", "ou", "ism", "ate", "iti", "ous", "ive", "ize"
        ]
        for suffix in suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.measure(stem) > 1:
                    if suffix == "ion":
                        if stem.endswith("s") or stem.endswith("t"):
                            return stem
                    else:
                        return stem
        return word

    def step5a(self, word):
        if word.endswith("e"):
            stem = word[:-1]
            m = self.measure(stem)
            if m > 1 or (m == 1 and not self.cvc(stem)):
                return stem
        return word

    def step5b(self, word):
        if self.measure(word) > 1 and self.ends_double_consonant(word) and word.endswith("l"):
            return word[:-1]
        return word

    def stem(self, word):
        word = word.lower()
        word = self.step1a(word)
        word = self.step1b(word)
        word = self.step1c(word)
        word = self.step2(word)
        word = self.step3(word)
        word = self.step4(word)
        word = self.step5a(word)
        word = self.step5b(word)
        return word
