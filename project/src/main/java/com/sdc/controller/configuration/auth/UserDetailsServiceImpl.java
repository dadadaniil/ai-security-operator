package com.sdc.controller.configuration.auth;

import com.sdc.controller.exception.custom.InvalidUserIdException;
import com.sdc.model.User;
import com.sdc.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.stereotype.Component;

@Component
public class UserDetailsServiceImpl implements UserDetailsService {
    private static final Logger logger = LoggerFactory.getLogger(UserDetailsServiceImpl.class);
    private final UserService userService;

    @Autowired
    public UserDetailsServiceImpl(UserService userService) {
        this.userService = userService;
    }

    @Override
    public UserDetails loadUserByUsername(String userId) {
        User user;
        try {
            user = userService.findUserById(Long.parseLong(userId));
        } catch (NumberFormatException _exception) {
            throw new InvalidUserIdException();
        }

        logger.info("User with id '{}' authenticated successfully", userId);
        return new CustomUserDetails(user);
    }
}
