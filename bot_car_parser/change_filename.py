def return_formatted_file_name(auction):
    arr = auction.split(' ')
    for _ in range(len(arr)):
        auction = auction.replace(' ', '_')
    return auction