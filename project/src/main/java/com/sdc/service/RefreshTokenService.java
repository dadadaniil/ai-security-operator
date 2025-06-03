package com.sdc.service;

import com.sdc.controller.exception.custom.InvalidRefreshTokenException;
import com.sdc.controller.exception.custom.NoSuchUserIdException;
import com.sdc.model.RefreshToken;
import com.sdc.model.User;
import com.sdc.repository.RefreshTokenRepository;
import com.sdc.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

@Service
public class RefreshTokenService {
    @Value("${application.security.jwt.refresh_expiration}")
    private long refreshExpiration;

    private final RefreshTokenRepository refreshTokenRepository;
    private final UserRepository userRepository;

    public RefreshTokenService(RefreshTokenRepository refreshTokenRepository, UserRepository userRepository) {
        this.refreshTokenRepository = refreshTokenRepository;
        this.userRepository = userRepository;
    }

    public Optional<RefreshToken> findByToken(String token) {
        return refreshTokenRepository.findByToken(token);
    }

    public RefreshToken createRefreshToken(Long userId) {
        final RefreshToken refreshToken = new RefreshToken();

        final User user = userRepository.findById(userId).orElseThrow(() -> NoSuchUserIdException.createWith(userId));
        refreshToken.setUser(user);
        refreshToken.setExpiryDate(Instant.now().plusMillis(refreshExpiration));
        refreshToken.setToken(UUID.randomUUID().toString());

        return refreshTokenRepository.save(refreshToken);
    }

    public RefreshToken verifyExpiration(RefreshToken token) {
        if (token.getExpiryDate().compareTo(Instant.now()) < 0) {
            refreshTokenRepository.delete(token);
            throw new InvalidRefreshTokenException();
        }

        return token;
    }

    @Scheduled(fixedRateString = "${application.table_clean_interval}")
    public void deleteOldRecords() {
        refreshTokenRepository.deleteAllByExpiryDateAfter(Instant.now());
    }
}
