
# email templates
class EmailTemplates:
    @staticmethod
    def OTPEmailTemplate(username:str, otp:int):
        return f"""hello {username},

        Thanks for registering to SNS - mangement app
        your OTP:{otp}
        
        If you are not not register for app ignore this email and 
        don't OTP with any one.

        Regards
        SNS-management app
        """