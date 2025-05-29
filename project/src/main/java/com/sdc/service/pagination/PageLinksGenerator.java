package com.sdc.service.pagination;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

@Service
public class PageLinksGenerator {
    @Value("${application.base.url}")
    private String baseUrl;

    public PageLinks generateLinks(String url, Page<?> page) {
        String previous = null;
        if (page.hasPrevious()) {
            final Pageable previousPage = page.previousPageable();
            final int num = previousPage.getPageNumber() + 1;
            previous = baseUrl + url + "?pageNum=" + num + "&pageSize=" + previousPage.getPageSize();
        }

        String next = null;
        if (page.hasNext()) {
            final Pageable nextPage = page.nextPageable();
            final int num = nextPage.getPageNumber() + 1;
            next = baseUrl + url + "?pageNum=" + num + "&pageSize=" + nextPage.getPageSize();
        }

        return new PageLinks(previous, next);
    }
}
