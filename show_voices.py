import pyttsx4
engine = pyttsx4.init()
voices = engine.getProperty('voices')
male_language_count = 0
female_language_count = 0
none_language_count = 0
for voice in voices:
    if voice.gender == 'male':
        # female language count
        male_language_count += 1
    elif voice.gender == 'female':
    	# female language count
        female_language_count +=1
    else:
        # None language count
        none_language_count += 1

print('Male gender language count : %d' %  male_language_count)
print('Female gender language count : %d' % female_language_count)
print('None gender language count : %d' % none_language_count)