# Logic for meeting scheduling:
# 1. sending an invite as per calendar: 8am - 6pm CDT
    # 1.1 check if conflicts in this time and exclude
    # 1.2 ask questions to user- what time to schedule / IS THIS TIME OK?
    # 1.3 if user says any then take random- if tells a slot then take meeting in that slot
        # write in prompt that schedule meets in the first half or similar
# 2. Schedule meeting as per the extracted slot using the API in intro1

