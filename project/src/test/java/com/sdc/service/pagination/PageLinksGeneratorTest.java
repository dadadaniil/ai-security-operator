package com.sdc.service.pagination;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

@ExtendWith(MockitoExtension.class)
public class PageLinksGeneratorTest {
    @InjectMocks
    private PageLinksGenerator pageLinksGenerator;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(pageLinksGenerator, "baseUrl", "http://example.com");
    }

    @DisplayName("Test for generateLinks() with only previous")
    @Test
    void testGenerateLinksWithOnlyPrevious() {
        final List<String> pageList = List.of("a", "b");
        final PageImpl<String> page = new PageImpl<>(pageList, PageRequest.of(3, 2), 6);

        final PageLinks pageLinks = pageLinksGenerator.generateLinks("/api/test", page);

        assertEquals("http://example.com/api/test?pageNum=3&pageSize=2", pageLinks.previous());
        assertNull(pageLinks.next());
    }

    @DisplayName("Test for generateLinks() with only next")
    @Test
    void testGenerateLinksWithOnlyNext() {
        final List<String> pageList = List.of("a", "b");
        final PageImpl<String> page = new PageImpl<>(pageList, PageRequest.of(0, 2), 6);

        final PageLinks pageLinks = pageLinksGenerator.generateLinks("/api/test", page);

        assertNull(pageLinks.previous());
        assertEquals("http://example.com/api/test?pageNum=2&pageSize=2", pageLinks.next());
    }

    @DisplayName("Test for generateLinks() with previous and next")
    @Test
    void testGenerateLinks() {
        final List<String> pageList = List.of("a", "b");
        final PageImpl<String> page = new PageImpl<>(pageList, PageRequest.of(1, 2), 6);

        final PageLinks pageLinks = pageLinksGenerator.generateLinks("/api/test", page);

        assertEquals("http://example.com/api/test?pageNum=1&pageSize=2", pageLinks.previous());
        assertEquals("http://example.com/api/test?pageNum=3&pageSize=2", pageLinks.next());
    }
}
