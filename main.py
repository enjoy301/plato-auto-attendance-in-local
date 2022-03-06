from check_lectures import CheckLectures as CL
import slack_notice as SN
from datetime import datetime


if __name__ == '__main__':
    cl = CL()
    cl.main()
    print_list = [str(datetime.now())]
    for key in cl.my_dict:
        print_list.append(key)
        if len(cl.my_dict[key]) == 0:
            print_list.append('EMPTY')
        else:
            print_list.append(', '.join(cl.my_dict[key]))
    SN.main(print_list)
