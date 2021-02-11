link = 'https://realty.yandex.ru/moskva/kupit/kvartira/studiya,1,2,3,4-i-bolee-komnatnie/?buildingClass=BUSINESS&deliveryDate=FINISHED&newFlat=YES&page=1'

print(link.split('&')[-1].split('=')[0])

if link.split('&')[-1].split('=')[0]:
    print(link.split('&')[-1].split('=')[-1])