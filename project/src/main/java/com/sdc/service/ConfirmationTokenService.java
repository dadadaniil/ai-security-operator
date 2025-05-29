package com.sdc.service;

import com.sdc.model.ConfirmationToken;
import com.sdc.repository.ConfirmationTokenRepository;
import com.sdc.util.Constants;
import lombok.NoArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;

@NoArgsConstructor
@Service
public class ConfirmationTokenService {
    private ConfirmationTokenRepository confirmationTokenRepository;
    private Constants constants;

    @Autowired
    public ConfirmationTokenService(
        ConfirmationTokenRepository confirmationTokenRepository,
        Constants constants
    ) {
        this.confirmationTokenRepository = confirmationTokenRepository;
        this.constants = constants;
    }

    @Scheduled(fixedRateString = "${application.table_clean_interval}")
    public void deleteOldRecords() {
        OffsetDateTime oneHourAgo = OffsetDateTime.now().minusHours(constants.tokenValidHours);
        confirmationTokenRepository.deleteAllByCreatedDateBefore(oneHourAgo);
    }

    public boolean isExpired(ConfirmationToken token) {
        OffsetDateTime expirationTime = OffsetDateTime.now().minusHours(constants.tokenValidHours);
        return token.getCreatedDate().isBefore(expirationTime) || token.getCreatedDate().isEqual(expirationTime);
    }

}
