from fastapi import status,HTTPException,Depends,Body,APIRouter
from app import db,models,oauth2, redis_service, otp_service, email_service
from sqlalchemy.orm import Session
import app.my_utils.utils as utils
import app.schemas as sch
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime
import datetime
from redis_service import redis_service
from email_service import email_service

router=APIRouter(tags=['Authentication'])
@router.post("/login",status_code=status.HTTP_202_ACCEPTED)
# method which log's in user if he has an account
# using the built-in schema for login 'OAuth2PasswordRequestForm'
# which is equivalent to our 'sch.UserLoginCred'
def loginUser(userCred:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(db.getDb)):
  # checks against the db for the username provided 
  isUserPresent=db.query(models.User).filter(models.User.username==userCred.username).first()
  # if not found tell the user not found
  if not isUserPresent:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user {userCred.username} not Found")
  # if found but he entered a wrong password tell him 
  if not utils.verifyPassword(userCred.password,isUserPresent.password):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"incorrect password")
  # if both username and password verfication is successfull call
  # the createAccessToken from oauth2 file which generates an jwt token
  tokenData={"userId":isUserPresent.id,"userName":isUserPresent.username}
  access_token=oauth2.createAccessToken(tokenData)
  # return the access token 
  return sch.TokenModel(id=isUserPresent.id,
                        username=isUserPresent.username,
                        accessToken=access_token,
                        tokenType="bearer" 
                        )

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2.oauth2_scheme)):
    try:
        # Decode the token to get the expiration time
        payload = jwt.decode(token, oauth2.SECRET_KEY, algorithms=[oauth2.ALGORITHM])
        expire_time = payload.get("expTime")
        if expire_time:
            # Calculate remaining time
            remaining_time = expire_time - datetime.now().timestamp()
            if remaining_time > 0:
                # Add token to blacklist with remaining time as TTL
                redis_service.add_to_blacklist(token, int(remaining_time))
        return {"message": "Successfully logged out"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: sch.ForgotPasswordSchema, db: Session = Depends(db.getDb)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        # To prevent user enumeration, we don't reveal if the user exists or not.
        # We'll just return a success message.
        return {"message": "If an account with this email exists, an OTP has been sent."}

    # Generate and save OTP
    otp = otp_service.generateOtp()
    otp_service.saveOtp(db, payload.email, otp, minutes=5)

    # Send OTP email
    try:
        await email_service.send_otp_email(to_email=payload.email, otp=otp)
        return {"message": "An OTP has been sent to your email."}
    except Exception as e:
        print(e) # for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error sending the email."
        )

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: sch.ResetPasswordSchema, db: Session = Depends(db.getDb)):
    # Verify OTP
    if not otp_service.checkOtp(db, payload.email, payload.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP."
        )

    # Find user and update password
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        # This should ideally not happen if OTP was validated correctly
        # but as a safeguard.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Hash the new password and update the user record
    hashed_password = utils.hashPassword(payload.new_password)
    user.password = hashed_password
    db.commit()

    return {"message": "Password has been reset successfully."}

