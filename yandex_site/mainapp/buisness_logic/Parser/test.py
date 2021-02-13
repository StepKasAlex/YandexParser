# link = 'https://realty.yandex.ru/moskva/kupit/kvartira/studiya,1,2,3,4-i-bolee-komnatnie/?buildingClass=BUSINESS&deliveryDate=FINISHED&newFlat=YES&page=1'
#
# print(link.split('&')[-1].split('=')[0])
#
# if link.split('&')[-1].split('=')[0]:
#     print(link.split('&')[-1].split('=')[-1])
#
#     print(f'Секции BS4 элемент - {sections_bs_markup}')
#     print(f'Название секции - {section_name}, название параметра - {param_name}')
#     print(f'То что в словаре со секциями по названию секции - {sections_bs_markup.get(section_name)}')
#
#     print(f'Секции - {sections_bs_markup}')
#     print(f'Разметка - {markup}')
#     print(f'СЕКЦИЯ - {section_name}')

string = 'I love you'

list_ = ['love', 'you']

for el in list_:
    string = string.replace(el, '')
    print(string)

print(string)