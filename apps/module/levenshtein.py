# 레벤슈타인 - 워드 거리
class Levenshtein:

    kor_begin = 44032
    kor_end = 55203
    chosung_base = 588
    jungsung_base = 28
    jaum_begin = 12593
    jaum_end = 12622
    moum_begin = 12623
    moum_end = 12643

    chosung_list = [ 'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 
            'ㅅ', 'ㅆ', 'ㅇ' , 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    jungsung_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 
            'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 
            'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 
            'ㅡ', 'ㅢ', 'ㅣ']

    jongsung_list = [
        ' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ',
            'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 
            'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 
            'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    jaum_list = ['ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄸ', 'ㄹ', 
                'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 
                'ㅃ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    moum_list = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 
                'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

    def leven_compose(self, chosung, jungsung, jongsung):
        char = chr(
            self.kor_begin +
            self.chosung_base * self.chosung_list.index(chosung) +
            self.jungsung_base * self.jungsung_list.index(jungsung) +
            self.jongsung_list.index(jongsung)
        )
        return char

    def leven_decompose(self ,c):
        # print('decompose에서 호출')
        # print(c)
        if not self.leven_character_is_korean(c):
            return c.upper() # return None에서 수정
        i = ord(c)
        if (self.jaum_begin <= i <= self.jaum_end):
            return (c, ' ', ' ')
        if (self.moum_begin <= i <= self.moum_end):
            return (' ', c, ' ')

        # decomposition rule
        i -= self.kor_begin
        cho  = i // self.chosung_base
        jung = ( i - cho * self.chosung_base ) // self.jungsung_base 
        jong = ( i - cho * self.chosung_base - jung * self.jungsung_base )    
        return (self.chosung_list[cho], self.jungsung_list[jung], self.jongsung_list[jong])

    def leven_character_is_korean(self, c):
        # print('characteriskorean에서 호출')
        # print(c)
        i = ord(c)
        return ((self.kor_begin <= i <= self.kor_end) or
                (self.jaum_begin <= i <= self.jaum_end) or
                (self.moum_begin <= i <= self.moum_end))

    def levenshtein(self, s1, s2, cost=None, debug=False):
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1, debug=debug)

        if len(s2) == 0:
            return len(s1)

        if cost is None:
            cost = {}

        # changed
        def substitution_cost(c1, c2):
            if c1 == c2:
                return 0
            return cost.get((c1, c2), 1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                # Changed
                substitutions = previous_row[j] + substitution_cost(c1, c2)
                current_row.append(min(insertions, deletions, substitutions))

            if debug:
                print(current_row[1:])

            previous_row = current_row

        return previous_row[-1]

    def jamo_levenshtein(self, s1, s2, debug=False):
        # print(len(s1))
        # print(len(s2))
        if len(s1) < len(s2):
            return self.jamo_levenshtein(s2, s1, debug)

        if len(s2) == 0:
            return len(s1)

        def substitution_cost(c1, c2):
            if c1 == c2:
                return 0
            return self.levenshtein(self.leven_decompose(c1), self.leven_decompose(c2))/3

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                # Changed
                substitutions = previous_row[j] + substitution_cost(c1, c2)
                current_row.append(min(insertions, deletions, substitutions))

            # if debug:
            # print(['%.3f'%v for v in current_row[1:]])

            previous_row = current_row

        return previous_row[-1]

    def return_correct_word(self, df, df_column, word):
        df['score'] = df.apply(lambda x: self.jamo_levenshtein(x[df_column], word), axis=1)
        return df.loc[df['score'].idxmin()][df_column]