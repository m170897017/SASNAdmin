def if_ip_valid(ip):
    ip = ip.split('.')
    # print ip
    print [len(number) <= 3 and 0 < int(number) < 255 for number in ip]
    return len(ip) == 4 and all([len(number) <= 3 and 0 < int(number) < 255 for number in ip])

print if_ip_valid('192.168.1.0001')
print if_ip_valid('0.0.0.0')