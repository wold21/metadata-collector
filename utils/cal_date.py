from datetime import datetime
def parse_incomplete_date(date_string):
    if not date_string:
        return None
    try:
        # YYYY 형식
        if len(date_string) == 4:
            return datetime.strptime(f"{date_string}-01-01", '%Y-%m-%d')
        # YYYY-MM 형식
        elif len(date_string) == 7:
            return datetime.strptime(f"{date_string}-01", '%Y-%m-%d')
        # YYYY-MM-DD 형식
        elif len(date_string) == 10:
            return datetime.strptime(date_string, '%Y-%m-%d')
        else:
            return None
    except ValueError:
        return None