package com.sdc.repository;

import com.sdc.model.ConfirmationToken;
import com.sdc.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.Optional;

@Repository
public interface ConfirmationTokenRepository extends JpaRepository<ConfirmationToken, Long> {
    Optional<ConfirmationToken> findByConfirmationToken(String confirmationToken);

    Optional<ConfirmationToken> findConfirmationTokenByUser(User user);

    @Transactional
    void deleteByTokenId(Long tokenId);

    @Transactional
    void deleteAllByCreatedDateBefore(OffsetDateTime localDateTime);

    @Transactional
    void deleteConfirmationTokensByUser(User user);
}
