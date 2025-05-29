package com.sdc.service;

import com.sdc.model.ConfirmationToken;
import com.sdc.model.User;
import com.sdc.util.Constants;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.annotation.Autowired;

import java.time.OffsetDateTime;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

@ExtendWith(MockitoExtension.class)
public class ConfirmationTokenServiceTest {

    @InjectMocks
    private ConfirmationTokenService confirmationTokenService;

    @Mock
    private Constants constants;

    private User user;

    @BeforeEach
    public void setup() {
        constants.tokenValidHours = 1;

        user = new User(
            1L,
            "UserName",
            "UserLastName",
            "email",
            "password",
            null,
            true,
            0L,
            0L,
            OffsetDateTime.now(),
            OffsetDateTime.now(),
            null,
            null
        );
    }

    @Test
    public void testIsExpiredWithExpiredToken() {
        ConfirmationToken confirmationToken = new ConfirmationToken(user);
        confirmationToken.setCreatedDate(OffsetDateTime.now().minusHours(5));
        boolean expired = confirmationTokenService.isExpired(confirmationToken);
        assertTrue(expired);
    }

    @Test
    public void testIsExpiredWithValidToken() {
        ConfirmationToken token = new ConfirmationToken();
        token.setCreatedDate(OffsetDateTime.now());
        assertFalse(confirmationTokenService.isExpired(token));
    }
}