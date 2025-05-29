package com.sdc.service;

import com.sdc.controller.exception.custom.InvalidRefreshTokenException;
import com.sdc.controller.exception.custom.NoSuchUserIdException;
import com.sdc.model.RefreshToken;
import com.sdc.model.User;
import com.sdc.repository.RefreshTokenRepository;
import com.sdc.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.context.TestPropertySource;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@TestPropertySource(properties = {
    "application.security.jwt.refresh_expiration=864000000"
})
public class RefreshTokenServiceTest {
    @Mock
    private UserRepository userRepository;

    @Mock
    private RefreshTokenRepository refreshTokenRepository;

    @InjectMocks
    private RefreshTokenService refreshTokenService;


    private Long userId;
    private User user;
    private RefreshToken refreshToken;
    private final long refreshExpiration = 864000000L;

    @BeforeEach
    void setUp() {
        userId = 1L;
        user = new User();
        user.setUserId(userId);

        refreshToken = new RefreshToken();
        refreshToken.setUser(user);
        refreshToken.setExpiryDate(Instant.now().plusMillis(refreshExpiration));
        refreshToken.setToken(UUID.randomUUID().toString());
    }

    @DisplayName("Test for createRefreshToken()")
    @Test
    void testCreateRefreshToken() {
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        when(refreshTokenRepository.save(any(RefreshToken.class))).thenReturn(refreshToken);

        RefreshToken createdToken = refreshTokenService.createRefreshToken(userId);

        assertNotNull(createdToken);
        assertEquals(user, createdToken.getUser());
        assertEquals(refreshToken.getExpiryDate(), createdToken.getExpiryDate());
        assertEquals(refreshToken.getToken(), createdToken.getToken());

        verify(userRepository, times(1)).findById(userId);
        verify(refreshTokenRepository, times(1)).save(any(RefreshToken.class));
    }

    @DisplayName("Test for createRefreshToken() with invalid user")
    @Test
    void testCreateRefreshTokenUserNotFound() {
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        assertThrows(NoSuchUserIdException.class, () ->
            refreshTokenService.createRefreshToken(userId)
        );

        verify(userRepository, times(1)).findById(userId);
        verify(refreshTokenRepository, times(0)).save(any(RefreshToken.class));
    }

    @DisplayName("Test for verifyExpiration() with valid token")
    @Test
    void testVerifyExpirationValidToken() {
        refreshToken.setExpiryDate(Instant.now().plusMillis(refreshExpiration));

        RefreshToken validToken = refreshTokenService.verifyExpiration(refreshToken);

        assertNotNull(validToken);
        assertEquals(refreshToken, validToken);
        verify(refreshTokenRepository, times(0)).delete(any(RefreshToken.class));
    }

    @DisplayName("Test for verifyExpiration() with expired token")
    @Test
    void testVerifyExpirationExpiredToken() {
        refreshToken.setExpiryDate(Instant.now().minusMillis(1000));
        assertThrows(InvalidRefreshTokenException.class, () ->
            refreshTokenService.verifyExpiration(refreshToken)
        );
        verify(refreshTokenRepository, times(1)).delete(refreshToken);
    }
}
