__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '6/10/2016'

import string
import re
from hanja import hangul

def rm_url(text):
    URL_PATTERN = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
    return re.sub(URL_PATTERN, " ", text)

def rm_specials(text, replace=" ", emoticon=False, exceptions=""):
    exceptions = set(exceptions)        # split into set element
    removed = "".join([" " if x in string.punctuation and x not in exceptions else x for x in text])
    return removed

def ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt):
    if new_check is False:
        if idx == phrase_cnt-1 and word_idx == word_cnt:
            pass
        else:
            formerTokenTag = ""
    else:
        new_check = False
    return new_check, formerTokenTag

def komoran_processing(komoran, complex_verb_set):
    tokenList = list()
    formerTokenTag = ""
    original_token = ""
    word_cnt = len(komoran)
    word_idx = 0
    for phrase in komoran:
        phrase_cnt = len(phrase)
        idx = 0
        word_idx += 1
        tokenWord = ""
        formerTag = ""
        new_check = False
        while idx < phrase_cnt:
            token = phrase[idx].getFirst().replace(" ", "") #remove white space in proper nouns
            if " " not in token and len(token) > 9:
                idx += 1
                new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                continue
            tag = phrase[idx].getSecond()
            ########## FIRST PHONEME
            if idx == 0 or (idx == 1 and formerTag == "XPN"):       #XPN: 체언접두사
                if formerTokenTag == "REMOVE_EC":
                    tokenList[-1] = "%s " % tokenList[-1]
                # To combine the former token and the current token
                elif formerTokenTag == "MAG":
                    tokenWord = tokenList[-1]
                    del tokenList[-1]
                elif formerTokenTag == "EC":
                    if tag not in {"VV", "VA", "VX"} or (tag in {"VV", "VA", "VX"} and token not in complex_verb_set):
                        tokenList[-1] = original_token
                        formerTokenTag = ""
                        original_token = ""
                # prefix(체언접두사)
                if tag == "XPN":
                    tokenWord = token
                    formerTag = tag
                    idx += 1
                    new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                    continue
                else:
                    # common noun, proper noun, root adverb and foreign language
                    if tag in {"NNG", "NNP", "SL", "XR", "MAG"}:
                        if tag == "SL":
                            token = token.lower()
                        if tag == "MAG":
                            if token in {"안", "못", "잘못"}:
                                formerTokenTag = "MAG"
                                new_check = True
                            else:
                                idx += 1
                                new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                                continue
                        elif tag == "NNP":
                            token = "%s " % token
                        elif formerTokenTag == "NNB" and token == "밖":
                            token = "밖에"
                            tokenWord = tokenWord.rstrip("_")
                            formerTokenTag = "JX"
                            new_check = True
                        else:
                            pass
                    # dependent nouns
                    elif tag == "NNB" and token in {"수", "지", "때문"}:
                        if token == "수" and formerTokenTag in {"VV", "VA", "VX"}:
                            formerTokenTag = "NNB1"
                        elif token == "수" and formerTokenTag not in {"VV", "VA", "VX"}:
                            formerTokenTag = ""
                            pass            # 사람의 '수' 등의 형태소분석 오류
                        elif token == "지" and formerTokenTag in {"VV", "VA", "VX"}:
                            formerTokenTag = "NNB2"
                        elif token == "때문":
                            formerTokenTag = "NNB3"
                        else:
                            formerTokenTag = ""
                            new_check = False
                            idx += 1
                            continue
                        new_check = True
                        try:
                            if formerTokenTag.startswith("NNB"):
                                token = "%s_%s" % (tokenList[-1], token)
                                del tokenList[-1]
                            else:
                                pass
                        except IndexError:      # not dependent nouns
                            formerTokenTag = ""
                            new_check = False
                            idx += 1
                            continue
                    # verb, adjective and auxiliary predicate
                    elif tag in ["VV", "VA", "VX"]:
                        if formerTokenTag == "EC":
                            token = "%s%s" % (tokenList[-1], "%s다" % token)
                            del tokenList[-1]
                        elif formerTokenTag == "JX":
                            if token == "없":        # 수밖에_없다
                                token = "_%s다" % token
                            else:
                                token = " %s다" % token
                        elif formerTokenTag.startswith("NNB"):
                            if formerTokenTag.endswith("1") and token in {"있", "없"}:    # 하다_수_있다
                                tokenWord = tokenList[-1]
                                token = "_%s다" % token
                                del tokenList[-1]
                            elif formerTokenTag.endswith("2") and token in {"모르", "않", "말"}:    # 하다_지_모르다
                                tokenWord = tokenList[-1]
                                token = "_%s다" % token
                                del tokenList[-1]
                            elif formerTokenTag.endswith("3"):      # 사랑_때문_자라다
                                tokenWord = tokenList[-1]
                                token = "_%s다" % token
                                del tokenList[-1]
                            else:
                                token = "%s다" % token
                        # only in case negative words
                        elif token in ["않", "없", "못하", "말", "싫", "주"]:
                            try:
                                token = "%s%s" % (tokenList[-1], "_%s다" % token)
                                del tokenList[-1]
                            except IndexError:
                                token = "_%s다" % token
                        else:
                            token = "%s다" % token
                        formerTokenTag = tag
                        new_check = True
                    elif formerTokenTag == "NNB1" and tag == "JX":
                        if token == "밖에":   # 수 밖에 = 수밖에
                            token = "%s%s" % (tokenList[-1].rstrip("_"), token)
                            del tokenList[-1]
                            formerTokenTag = "JX"
                            new_check = True
                        elif token == "도":  # 갈 수도 있다 = 가다_수_있다
                            new_check = True
                    else:
                        # just pass the rest
                        idx += 1
                        formerTag = tag
                        new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                        continue
                    tokenWord += token
                    formerTag = tag
                    # checking 'formerTokenTag' to be newly assigned
                    new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
            ########## FROM SECOND PHONEME
            else:
                if formerTokenTag == "REMOVE_EC":
                    tokenWord = "%s " % tokenWord
                elif formerTokenTag.startswith("NNB") and tag not in {"VV", "VA", "VX"}:
                    tokenWord = "%s " % tokenWord
                if formerTag in ["ETM", "ETN"]:     # ETM: 관성형전성어미, ETN: 명사형전성어미
                    tokenWord = "%s " % tokenWord
                # common noun, proper noun, root and foreign language, suffix(noun) and dependent noun
                if tag in {"NNG", "NNP", "XR", "SL", "NNB", "XSN"}:
                    if tag == "SL":
                        token = token.lower()
                    if tag == "NNP":
                        if formerTag == "NNP":
                            tokenWord = "%s%s " % (tokenWord, token)
                        else:
                            tokenWord = "%s %s " % (tokenWord, token)
                    elif tag == "NNB":
                        if token in {"수", "지", "때문"}:
                            if token == "수":
                                if formerTag in {"VV", "VA", "VX"}:
                                    tokenWord = "%s_%s" % (tokenWord.strip(), token)
                                    formerTokenTag = "NNB1"
                                else:
                                    tokenWord = "%s %s" % (tokenWord.strip(), token)
                            elif token == "지" and formerTag in {"VV", "VA", "VX"}:
                                tokenWord = "%s_%s" % (tokenWord.strip(), token)
                                formerTokenTag = "NNB2"
                            elif token == "때문":
                                tokenWord = "%s_%s" % (tokenWord.strip(), token)
                                formerTokenTag = "NNB3"
                            else:
                                pass
                            new_check = True
                        else:
                            pass
                    else:
                        tokenWord += token
                # 부정지정사 '아니'
                elif tag == "VCN":
                    tokenWord = "%s_%s다" % (tokenWord, token)
                # 수 밖에 = 수밖에
                elif (formerTokenTag == "NNB1" or formerTag == "NNB1") and tag == "JX":
                    if token == "밖에":
                        tokenWord = "%s%s" % (tokenWord.rstrip("_"), token)
                        formerTokenTag = "JX"
                        new_check = True
                    elif token == "도":
                        new_check = True
                # suffix(adjective and verb)
                elif tag in {"XSA", "XSV"}:
                    token = "%s다" % token
                    tokenWord += token
                # connective endings
                elif tag == "EC":
                    original_token = tokenWord
                    newToken = tokenWord.rstrip("다")
                    try:
                        jong = hangul.separate(newToken[-1])     #마지막 글자 분해
                    except IndexError:
                        idx += 1
                        formerTag = tag
                        new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                        continue
                    if token in {"아", "어"}:
                        if formerTag == "VCP":
                            idx += 1
                            formerTag = tag
                            new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                            continue
                        # 받침없음
                        if jong[-1] == 0:
                            if jong[1] == 20 and token == "어":       # 달리+어=달려
                                newJong = hangul.build(jong[0], 6, jong[-1])
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = newToken
                            elif jong[1] == 18 and jong[0] == 5:       # '르' 불규칙: 마르+아=말라
                                tmp = hangul.separate(newToken[-2])
                                newJong = hangul.build(tmp[0], tmp[1], 8)
                                tmp2 = hangul.separate(token)
                                newJong2 = hangul.build(5, tmp2[1], tmp2[2])
                                if len(newToken) == 2:      # 마르, 오르, 바르..
                                    newToken = "%s%s" % (newJong, newJong2)
                                else:
                                    newToken = "%s%s%s" % (newToken[:-2], newJong, newJong2)
                                tokenWord = newToken
                            elif jong[1] == 18 and token == "어":       # 'ㅡ' 불규칙: 쓰+어=써
                                newJong = hangul.build(jong[0], 4, jong[-1])
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = newToken
                            elif jong[1] == 13 and token == "어":       # 세우+어=세워
                                newJong = hangul.build(jong[0], 14, jong[-1])
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = newToken
                            elif jong[1] == 8 and token == "아":     # 따라오+아=따라와
                                newJong = hangul.build(jong[0], 9, jong[-1])
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = newToken
                            elif jong[1] == 11 and token == "어":       # 되+어=되어
                                newToken = "%s%s" % (newToken, "어")
                                tokenWord = newToken
                            elif jong == (18,0,0) and token in {"아", "어"}:
                                if len(newToken) == 1:
                                    tokenWord = "해"
                                else:
                                    tokenWord = "%s해" % newToken[:-1]
                            else:
                                tokenWord = newToken        # 펴, 자
                        # 받침있음
                        else:
                            # '빨개야', '파래야' 등의 'ㅎ' 탈락은 형태소분석 자체가 잘 되지 않아 불규칙 적용하지 않음
                            # '묻다'는 '땅에 묻다'와 '물어보다'의 의미가 구분되지 않아 불규칙 적용하지 않음
                            if jong[-1] == 7 and \
                                    (newToken[-1] in ("걷", "싣", "듣") or newToken[-2:] in ("깨닫", "일컫")):  # ㄷ받침
                                newJong = hangul.build(jong[0], jong[1], 8)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                            elif jong[-1] == 19 and \
                                    (newToken[-1] in ("긋", "낫", "붓", "잇", "젓", "짓")):  # ㅅ받침
                                newJong = hangul.build(jong[0], jong[1], 0)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                            elif jong[-1] == 17 \
                                    and newToken[-1] not in ("입", "잡", "씹", "좁", "접", "뽑"):    # ㅂ받침: 눕+어=누워
                                newJong = hangul.build(jong[0], jong[1], 0)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                if token == "어":
                                    token = "워"
                                elif token == "아":
                                    token = "와"
                            tokenWord = "%s%s" % (newToken, token)
                        formerTokenTag = "EC"
                        new_check = True
                    elif token in {"어야", "아야", "어다", "아다"}:
                        ending = token[-1]
                        if jong[-1] == 0:           # 받침 없음
                            if jong[1] == 20 and token.startswith("어"):       # 달려야, 마셔야
                                newJong = hangul.build(jong[0], 6, jong[-1])
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s%s" % (newToken[:-1], newJong, ending)
                                tokenWord = newToken
                            elif jong[1] == 18 and jong[0] == 5:       # '르' 불규칙: 마르+아야=말라야
                                tmp = hangul.separate(newToken[-2])
                                newJong = hangul.build(tmp[0], tmp[1], 8)
                                tmp2 = hangul.separate(token[0])
                                newJong2 = hangul.build(5, tmp2[1], tmp2[2])
                                if len(newToken) == 2:      # 마르, 오르, 바르..
                                    newToken = "%s%s%s" % (newJong, newJong2, ending)
                                else:
                                    newToken = "%s%s%s%s" % (newToken[:-2], newJong, newJong2, ending)
                                tokenWord = newToken
                            elif jong[1] == 18 and token.startswith("어"):       # 'ㅡ' 불규칙: 쓰+어야=써야
                                newJong = hangul.build(jong[0], 4, jong[-1])
                                if len(newToken) == 1:
                                    newToken = "%s%s" % (newJong, ending)
                                else:
                                    newToken = "%s%s%s" % (newToken[:-1], newJong, ending)
                                tokenWord = newToken
                            elif jong[1] == 13 and token.startswith("어"):       # 세우+어야=세워야
                                newJong = hangul.build(jong[0], 14, jong[-1])
                                if len(newToken) == 1:
                                    newToken = "%s%s" % (newJong, ending)
                                else:
                                    newToken = "%s%s%s" % (newToken[:-1], newJong, ending)
                                tokenWord = newToken
                            elif jong[1] == 8 and token.startswith("아"):       # 따라오+아야=따라와야
                                newJong = hangul.build(jong[0], 9, jong[-1])
                                if len(newToken) == 1:
                                    newToken = "%s%s" % (newJong, ending)
                                else:
                                    newToken = "%s%s%s" % (newToken[:-1], newJong, ending)
                                tokenWord = newToken
                            elif jong == (18,0,0) and (token.startswith("아") or token.startswith("어")):     # 해야
                                if len(newToken) == 1:
                                    tokenWord = "해%s" % ending
                                else:
                                    tokenWord = "%s해%s" % (newToken[:-1], ending)
                            else:
                                tokenWord = "%s%s" % (newToken, ending)        # 펴야, 자야
                        # 받침 있음
                        elif jong[-1] != 0:
                            if jong[-1] == 17 \
                                    and newToken[-1] not in ("입", "잡", "씹", "좁", "접", "뽑"):    # ㅂ받침: 눕+어=누워
                                newJong = hangul.build(jong[0], jong[1], 0)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                if token.startswith("어"):       # 아름다워야
                                    tokenWord = "%s워%s" % (newToken, ending)
                                elif token.startswith("아"):     # 고와야
                                    tokenWord = "%s와%s" % (newToken, ending)
                            elif jong[-1] == 19 and \
                                    (newToken[-1] in ("긋", "낫", "붓", "잇", "젓", "짓")):  # ㅅ받침
                                newJong = hangul.build(jong[0], jong[1], 0)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = "%s%s" % (newToken, token)
                            elif jong[-1] == 7 and \
                                    (newToken[-1] in ("걷", "싣", "듣") or newToken[-2:] in ("깨닫", "일컫")):      # ㄷ받침
                                newJong = hangul.build(jong[0], jong[1], 8)
                                if len(newToken) == 1:
                                    newToken = newJong
                                else:
                                    newToken = "%s%s" % (newToken[:-1], newJong)
                                tokenWord = "%s%s%s" % (newToken, token[0], ending)
                            else:
                                tokenWord = "%s%s" % (newToken, token)
                        formerTokenTag = "EC"
                        new_check = True
                    elif token.endswith("지") and formerTag in {"VV", "VA", "VX"}:       # 하다_지_모른다
                        tokenWord = "%s다_지_" % newToken
                        formerTokenTag = "EC"
                        new_check = True
                    else:
                        formerTokenTag = "REMOVE_EC"
                        new_check = True
                # verb and adjective
                elif tag in ["VV", "VA", "VX"]:
                    if formerTokenTag == "EC":
                        if tag == "VX" and token == "가지":  # 해가지고, 떠가지고 = 하다, 뜨다
                            tokenWord = original_token
                        else:
                            tokenWord = "%s%s" % (tokenWord, token+"다")
                    elif formerTokenTag.startswith("NNB"):
                        if formerTokenTag.endswith("1") and token in {"있", "없"}:    # 하다_수_있다
                            tokenWord = "%s_%s다" % (tokenWord, token)
                        elif formerTokenTag.endswith("2") and token in {"모르", "않", "말"}:    # 하다_지_모르다
                            tokenWord = "%s_%s다" % (tokenWord, token)
                        elif formerTokenTag.endswith("3"):      # 사랑_때문_자라다
                            tokenWord = "%s_%s다" % (tokenWord, token)
                        else:
                            tokenWord += "%s다" % token
                    elif formerTokenTag == "JX":
                        if token == "없":
                            tokenWord += "_%s다" % token
                        else:
                            tokenWord += " %s다" % token
                    else:
                        if tag in ("VX", "VA") and token in ["않", "없", "못하", "말", "주"]:
                            tokenWord += "_%s다" % token
                        else:   # rest all tag including VX
                            # insert white space if V-V or VA-VA case(grammar error)
                            if formerTokenTag == tag:
                                tokenWord += " %s다" % token
                            else:
                                tokenWord += "%s다" % token
                    formerTokenTag = tag
                    new_check = True
                # adverb
                elif tag == "MAG" and token == "못":
                    tokenWord += "_%s" % token
                elif tag == "MAG" and token == "없이":
                    tokenWord = "%s없다" % tokenWord
                # JKB: 부사격조사
                elif tag == "JKB" and token == "같이":
                    tokenWord = "%s같다" % tokenWord
                else:
                    idx += 1
                    formerTag = tag
                    new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
                    continue
                formerTag = tag
                new_check, formerTokenTag = ending_check(new_check, formerTokenTag, idx, word_idx, phrase_cnt, word_cnt)
            idx += 1
        tokenList.append(tokenWord.strip())
    # if it's the last word in 'Komoran'
    if formerTokenTag == "EC":
        tokenList[-1] = original_token
    finalToken = " ".join([a for a in tokenList if a not in {"", "하다", "암트다"}])        # stop word
    if "안 하다" in finalToken:
        finalToken = finalToken.replace("안 하다", "안하다")
    for neg in {"없다", "않다", "못하다", "안하다"}:
        if neg == finalToken:
            continue
        if " _%s" % neg in finalToken:
            finalToken = finalToken.replace(" _%s" % neg, " %s" % neg)
        if " %s" % neg in finalToken:
            finalToken = finalToken.replace(" %s" % neg, "_%s" % neg)
        if (" _%s" % neg) in finalToken:
            finalToken = finalToken.replace((" _%s" % neg), ("_%s" % neg))
    finalToken = finalToken.strip("_").replace("__", "_").replace(" _", " ").replace("_ ", " ")
    return re.sub(r"\s+", " ", finalToken)
