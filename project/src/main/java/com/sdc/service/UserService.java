package com.sdc.service;

import com.sdc.model.User;
import com.sdc.model.dto.PasswordResetDto;
import com.sdc.model.dto.RequestResetDto;
import com.sdc.model.dto.UserDto;

public interface UserService {
    User saveUser(UserDto user);

    void confirmEmail(String confirmationToken);

    void resendConfirmEmail(Long userId);

    boolean authenticateUser(String email, String password);

    void requestPasswordReset(RequestResetDto requestResetDto);

    User resetPassword(PasswordResetDto passwordResetDto);
    User findUserById(long id);
    User findUserByEmail(String email);
}
