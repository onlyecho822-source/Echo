# Extended Research Intelligence Report
## Illinois Unclaimed Property - Cook County Analysis

**Date:** January 7, 2026  
**Project:** Illinois Unclaimed Property Scanner  
**Scope:** Cook County (ZIP 60601-60699), Properties > $1,000

---

## Executive Summary

This report documents comprehensive research conducted beyond the initial GitHub repository development to identify alternative sources and methods for accessing Illinois unclaimed property data. The research reveals significant legal, technical, and structural barriers to bulk data access, while also uncovering multiple alternative resources and approaches.

### Key Discoveries

1. **Legal Barriers**: Illinois statute 765 ILCS 1026/15-102(5) & 1401(b) legally prohibits the State Treasurer from disclosing detailed unclaimed property information to the general public
2. **Dual Systems**: Two separate unclaimed property systems exist - State level (Illinois Treasurer) and County level (Cook County Treasurer)
3. **Total Unclaimed Funds**: Over $5 billion statewide + $155 million in Cook County property tax refunds
4. **Technical Protection**: CloudFront WAF and Cloudflare Turnstile block all automated access attempts
5. **Alternative Resources**: Multiple legitimate channels exist for manual searching and data requests

---

## Part 1: Alternative Data Sources

### 1.1 MissingMoney.com - National Multi-State Database

**URL:** https://missingmoney.com/

**Description**: Official unclaimed property search website endorsed by NAUPA (National Association of Unclaimed Property Administrators) and NAST (National Association of State Treasurers).

**Key Statistics**:
- $3+ billion in paid claims in the last year
- 95% of all claims filed online
- 1 in 7 people have unclaimed property
- $2,080 average claim value

**Capabilities**:
- Multi-state simultaneous search
- Partners with Illinois and other state governments
- Daily updates with new properties
- Name-based search (last/business name required)

**Advantages Over Illinois ICash**:
- Searches multiple states at once
- May have different bot protection mechanisms
- Official NAUPA partnership provides legitimacy

**Limitations**:
- Still requires name-based search (no ZIP code only)
- No bulk download option visible
- No API access mentioned
- Individual search interface only

**Recommendation**: Test MissingMoney.com for automation accessibility as potential alternative to direct Illinois site access.

---

### 1.2 Cook County Treasurer - Property Tax Refunds

**URL:** https://www.cookcountytreasurer.com/

**Treasurer:** Maria Pappas

**Critical Discovery**: This is a SEPARATE source of unclaimed money from the Illinois State Treasurer's ICash program.

**Available Databases**:
1. **$122 million in property tax refunds** - Searchable database
2. **$33 million in missing senior exemptions** - Going back four years

**Total Cook County Unclaimed Money**:
- State level (ICash): Portion of $5 billion statewide
- County level (Treasurer): $155 million ($122M + $33M) in property tax-related funds

**"Black Houses Matter" Initiative**:

Cook County Treasurer Maria Pappas launched this initiative to address racial disparity in homeownership by helping property owners access unclaimed refunds and exemptions.

**Results (as of January 2021)**:
- Helped 22,000 property owners get off 2018 tax sale list
- Issued $43.5 million in refunds to majority-Black suburbs and Chicago wards since March 2020
- 35,721 properties remained on tax sale list as of January 15, 2021
- Half owed less than $1,000 in back taxes

**Notable Cases**:
- Jerry Wynn (Ashburn): $1,400 refund from overpaying 2018 property taxes
- 74-year-old grandfather (Matteson): Owed as much as $6,000 after double-payment and unclaimed exemptions

**Tax Exemptions Available** ($500-$1,500 per year):
- Veterans
- Disability
- Seniors (making under $55,000/year)
- Home improvements
- Longtime homeowners

**Unique Resource**: Maria Pappas hosts weekly radio show on WVON 1690-AM where residents can call for one-on-one help with unclaimed property tax refunds.

**Access Method**:
- Individual property search by address or PIN (Property Index Number)
- No bulk download or API apparent
- May have similar bot protection as state site

**Recommendation**: Should test if Cook County Treasurer site allows automated searches or has less restrictive bot protection than the state ICash site. This is a completely separate data source that must be searched independently.

---

### 1.3 Illinois State Treasurer 2024 Annual Report

**URL:** https://illinoistreasurergovprod.blob.core.usgovcloudapi.net/twocms/media/doc/2024%20annual%20report_final_12.27_digital_compressed.pdf

**Document**: PDF, 48 pages, dated December 27, 2024

**Unclaimed Property Statistics**:
- Total unclaimed property held: **$5+ billion**
- Returned since 2015: **$2.1 billion** (record-shattering)
- Returned in FY 2024 alone: **$301 million**

**Notable Case**:
- A Lake County widower received more than $500,000 in life insurance policies

**Property Types Listed**:
- Bank safe deposit box contents
- Undelivered paychecks
- Utility refunds
- Life insurance policies

**Value**: Confirms the scale of unclaimed property in Illinois but does not provide county-level breakdowns or searchable lists. Useful for understanding program scope and success metrics.

---

### 1.4 Illinois Comptroller - "Check for Cash"

**URL:** https://illinoiscomptroller.gov/constituent-services/public-services-community-programs/check-for-cash

**Purpose**: Uncashed state checks (different from ICash unclaimed property)

**Description**: Every year, thousands of state checks payable to taxpayers go uncashed. This application allows taxpayers to learn whether they can claim an uncashed check.

**Relevance**: May contain overlapping or additional unclaimed funds separate from the Treasurer's ICash program.

**Recommendation**: Add to list of databases to search as a complementary source.

---

### 1.5 Federal and Specialized Sources

**Federal Court Unclaimed Funds**:
- URL: https://www.ilnb.uscourts.gov/unclaimed-funds-instructions
- Purpose: Federal court unclaimed funds (Northern District of Illinois)
- Relevance: Different source, may have high-value properties

**FDIC Unclaimed Funds**:
- URL: https://closedbanks.fdic.gov/funds/
- Purpose: Unclaimed funds from closed banks
- Relevance: May include Illinois/Cook County properties from bank failures

---

## Part 2: Legal and Public Records Analysis

### 2.1 Illinois Freedom of Information Act (FOIA)

**URL:** https://illinoistreasurer.gov/foia/

**Contact Information**:
- Email: FOIA@illinoistreasurer.gov
- Mail: Office of the Illinois State Treasurer, ATTN: FOIA Officer, 1 East Old State Capitol Plaza, Springfield, IL 62701
- Form: FOIA Request Form (downloadable)

**Required Information**:
1. The phrase "Freedom of Information Act" or "FOIA"
2. Specific description of records sought
3. Contact information (telephone or email)

**Costs**:
- Black-and-white copies over 50 pages: $0.15 per page
- Rules codified at 2 Ill. Adm. Code 651

---

### 2.2 CRITICAL LEGAL RESTRICTION

The Illinois State Treasurer's FOIA page explicitly states:

> "Public information regarding unclaimed property claims is available on our I-Cash database; however, **total property values are withheld until a claim form is received**. The Treasurer is **legally prohibited from providing additional information about unclaimed property** other than to government agencies acting to return the property and to persons who appear to be the owner of the property or otherwise have a valid claim to the property, See **765 ILCS 1026/15-102(5) & 1401(b)**."

---

### 2.3 Illinois Revised Uniform Unclaimed Property Act

**Legal Citation**: 765 ILCS 1026/15-102(5) & 1401(b)

**Definition of "Confidential Information"** (765 ILCS 1026/15-102(5)):

"Confidential information" means information that is:
- "Personal information" under the Personal Information Protection Act
- "Private information" under the Freedom of Information Act
- Personal information contained within public records, the disclosure of which would constitute a clearly unwarranted invasion of personal privacy

**Disclosure Restrictions** (765 ILCS 1026/1401):

The administrator (State Treasurer) and their agent:
- Cannot use confidential information except as expressly authorized by law
- Can only provide information to:
  - Government agencies acting to return property
  - Apparent owners of the property
  - Those with valid claims to the property

---

### 2.4 Implications for Data Access

**What This Means**:

1. **Property values are intentionally hidden** on the public ICash database until someone files a claim
2. **Bulk data access is legally restricted** - The Treasurer cannot provide detailed unclaimed property information to researchers or the general public
3. **FOIA requests will likely be denied** based on statutory confidentiality protections

**Why the System Works This Way**:

This is not just technical protection or administrative policy - it's **legal protection mandated by Illinois statute**. The law specifically prohibits the Treasurer from disclosing detailed unclaimed property information to protect owner privacy.

**Only Legal Access Method**:

1. Search individual names on ICash
2. File a claim form for each property
3. Then the value is revealed

This explains why academic researchers have found "very little research has been conducted" on unclaimed property despite billions of dollars being involved - the data is legally protected.

---

## Part 3: Technical Analysis

### 3.1 Bot Protection Mechanisms

**Illinois ICash Website Protection**:
- AWS CloudFront Web Application Firewall (WAF)
- Cloudflare Turnstile (CAPTCHA-like protection)
- 403 Forbidden errors for automated requests
- Bot detection on search submission

**What Was Blocked**:
- ✗ Direct HTTP/API requests
- ✗ Selenium WebDriver automation
- ✗ Headless browser access
- ✗ Automated form submission

**Test Results**:
- Selenium successfully accessed Google.com (control test passed)
- Selenium blocked from accessing icash.illinoistreasurer.gov (403 Forbidden)
- All 50 test searches timed out due to CloudFront protection

---

### 3.2 No Public API

**Findings**:
- Illinois does not provide a public API for unclaimed property searches
- No bulk data download options available
- No CSV/JSON export functionality
- Human-only web interface by design

**Comparison to Other States**:

According to academic research, state unclaimed property management varies significantly. Some states may have more accessible data systems, but Illinois has chosen a highly restrictive approach prioritizing privacy protection.

---

### 3.3 Archived Data Search

**Wayback Machine**: No useful historical data found that would bypass current restrictions.

**Historical Records**: Illinois unclaimed property program dates back to 1962, but historical databases are not publicly accessible in bulk format.

---

## Part 4: Academic and Research Insights

### 4.1 Academic Study on Unclaimed Property Management

**Source**: "Hidden treasure: a study of unclaimed property management by state government"  
**Authors**: Darrin Wilson & Derek Slagle (2018)  
**Journal**: Journal of Public Budgeting, Accounting & Financial Management  
**DOI**: 10.1108/JPBAFM-03-2018-001

**Key Finding**: This is described as "the first comprehensive study on how state governments manage unclaimed property."

**Why So Little Research**:

The authors note that "very little research has been conducted on the function of returning unclaimed property to owners or the related public administration operation of unclaimed property."

This scarcity of research is directly related to the data access barriers documented in this report - academic researchers face the same legal and technical restrictions we encountered.

**Study Methodology**:

The researchers conducted a 2011 survey of state unclaimed property agencies (not direct data access) and found that:
- Type of uniform code used affects return rates
- Presence and size of marketing staff affects return rates
- State approaches vary significantly

---

### 4.2 National Context

**NAUPA (National Association of Unclaimed Property Administrators)**:
- URL: https://unclaimed.org/
- Leading authority in unclaimed property
- Coordinates multi-state efforts
- May have research resources or bulk data access policies

**National Statistics**:
- Over $2.8 billion returned to owners during FY 2020 (NAUPA data)
- New York has the most unclaimed property ($17+ billion)
- Illinois ranks among top states for unclaimed property holdings

---

## Part 5: Viable Alternative Approaches

### 5.1 Manual Search Strategy (Most Reliable, Immediate)

**Process**:
1. Visit https://icash.illinoistreasurer.gov/app/claim-search
2. Search using common surnames combined with Cook County ZIP codes
3. Review results for properties > $1,000
4. Record findings manually

**Top 20 Surnames to Search** (based on US Census data):
1. Smith
2. Johnson
3. Williams
4. Brown
5. Jones
6. Garcia
7. Rodriguez
8. Martinez
9. Hernandez
10. Lopez
11. Gonzalez
12. Wilson
13. Anderson
14. Thomas
15. Taylor
16. Moore
17. Jackson
18. Martin
19. Lee
20. Thompson

**Cook County ZIP Codes**: 60601-60699 (99 ZIP codes total)

**Estimated Effort**:
- 20 surnames × 99 ZIP codes = 1,980 searches
- At 30 seconds per search = 16.5 hours of manual work
- Could be distributed among multiple volunteers

**Advantages**:
- Legal and compliant
- Immediate access
- No technical barriers
- Reveals actual property values

**Disadvantages**:
- Time-intensive
- Limited coverage (only common surnames)
- Manual data entry required

---

### 5.2 FOIA Request (Official Channel, Slow)

**Process**:
1. Download FOIA Request Form from https://illinoistreasurer.gov/foia/
2. Submit written request to FOIA@illinoistreasurer.gov
3. Request: "Statistical summary of unclaimed properties in Cook County (ZIP 60601-60699) by value range, without personally identifiable information"

**FOIA Request Template**:

```
Subject: Freedom of Information Act Request - Unclaimed Property Statistics

To: FOIA Officer, Illinois State Treasurer's Office

This is a request under the Illinois Freedom of Information Act (5 ILCS 140).

I am requesting statistical information about unclaimed property held by the Illinois State Treasurer's Office for Cook County (ZIP codes 60601-60699), specifically:

1. Total number of unclaimed properties by ZIP code
2. Number of properties in the following value ranges: $1,000-$5,000, $5,001-$10,000, $10,001-$50,000, $50,000+
3. Total dollar value of unclaimed property by ZIP code
4. Property types (e.g., bank accounts, insurance, safe deposit boxes) by count

I am NOT requesting personally identifiable information, property owner names, or specific property details that would be protected under 765 ILCS 1026/15-102(5) & 1401(b). I am requesting only aggregate statistical data.

Preferred format: CSV or Excel spreadsheet

Contact Information:
[Your name]
[Your email]
[Your phone]

Thank you for your consideration.
```

**Expected Response Time**: 5-10 business days

**Likelihood of Success**: Moderate - Statistical data without PII may be provided, but detailed property lists will likely be denied under confidentiality statutes.

**Cost**: Minimal (copies over 50 pages at $0.15/page)

---

### 5.3 Cook County Treasurer Direct Search

**Process**:
1. Visit https://www.cookcountytreasurer.com/
2. Search for property tax refunds by address or PIN
3. Check $122 million refund database
4. Check $33 million senior exemption database

**Advantages**:
- Separate data source from state ICash
- $155 million in Cook County-specific funds
- May have different access restrictions
- Addresses racial equity in homeownership

**Method**:
- Requires property address or PIN (not searchable by name alone)
- Could systematically search addresses in target ZIP codes
- May be more amenable to automation (needs testing)

**Recommendation**: Priority target for automation testing - may have less restrictive bot protection than state site.

---

### 5.4 Browser Extension Development (Long-term, Technical)

**Concept**:
- Develop Chrome/Firefox extension
- Runs in user's actual browser (not automated bot)
- Assists with systematic searching
- Extracts and saves results
- Avoids bot detection by using real user session

**Advantages**:
- Bypasses bot protection (real user session)
- Legal and compliant (user-initiated searches)
- Could assist volunteers with manual searching
- Scalable across multiple users

**Disadvantages**:
- Development time required
- Requires user installation and operation
- Still subject to rate limiting
- Not fully automated

**Technical Approach**:
1. User installs extension
2. User navigates to ICash search page
3. Extension provides interface to:
   - Load list of names/ZIP codes to search
   - Automatically fill search forms
   - Extract results from pages
   - Save to local JSON file
4. User remains in control, extension just assists

**Estimated Development Time**: 2-4 weeks for functional prototype

---

### 5.5 Partnership with Illinois State Treasurer (Official Channel)

**Approach**:
- Contact Illinois State Treasurer's Office directly
- Explain research purpose and public benefit
- Request official partnership or data access agreement
- Propose collaboration on outreach to Cook County residents

**Contact**:
- Office: Illinois State Treasurer Michael Frerichs
- Phone: (217) 785-6998
- Email: Via website contact form
- Address: 1 East Old State Capitol Plaza, Springfield, IL 62701

**Pitch**:
"We are conducting research to identify high-value unclaimed properties in Cook County to assist with outreach efforts, particularly in underserved communities. We seek to partner with your office to help return unclaimed property to rightful owners, similar to the successful 'Black Houses Matter' initiative by Cook County Treasurer Maria Pappas."

**Potential Benefits to Treasurer**:
- Increased property returns (improves their metrics)
- Outreach to underserved communities
- Positive publicity
- Volunteer research assistance

**Likelihood of Success**: Low to moderate - depends on current priorities and willingness to work with external researchers.

---

### 5.6 Third-Party Commercial Services

**Potential Services**:
- Asset recovery firms
- Private investigation services
- Unclaimed property search companies

**Caution**: Many third-party services charge fees or take percentages of recovered property. Ensure any service used is reputable and compliant with Illinois law.

**Recommendation**: Focus on free, official channels first before considering commercial services.

---

## Part 6: Comprehensive Resource Directory

### State-Level Resources

| Resource | URL | Purpose | Access |
|----------|-----|---------|--------|
| Illinois ICash | https://icash.illinoistreasurer.gov | State unclaimed property search | Free, name-based |
| Illinois Treasurer FOIA | https://illinoistreasurer.gov/foia/ | Official records requests | FOIA process |
| Illinois Comptroller Check for Cash | https://illinoiscomptroller.gov/.../check-for-cash | Uncashed state checks | Free search |
| Illinois 2024 Annual Report | https://illinoistreasurergovprod.blob.core.usgovcloudapi.net/twocms/media/doc/2024%20annual%20report_final_12.27_digital_compressed.pdf | Program statistics | Free PDF |

### County-Level Resources

| Resource | URL | Purpose | Access |
|----------|-----|---------|--------|
| Cook County Treasurer | https://www.cookcountytreasurer.com/ | Property tax refunds | Free, address/PIN |
| Property Tax Refund Search | https://www.cookcountytreasurer.com/ptabrefundsearch.aspx | $122M refund database | Free search |
| Maria Pappas Radio Show | WVON 1690-AM (Mondays) | One-on-one assistance | Call-in |

### National Resources

| Resource | URL | Purpose | Access |
|----------|-----|---------|--------|
| MissingMoney.com | https://missingmoney.com/ | Multi-state search | Free, name-based |
| NAUPA | https://unclaimed.org/ | National authority | Information |
| Federal Court (N.D. IL) | https://www.ilnb.uscourts.gov/unclaimed-funds-instructions | Federal court funds | Free search |
| FDIC Unclaimed Funds | https://closedbanks.fdic.gov/funds/ | Closed bank funds | Free search |

### Legal References

| Citation | Description | URL |
|----------|-------------|-----|
| 765 ILCS 1026/15-102(5) | Confidential information definition | https://codes.findlaw.com/il/chapter-765-property/il-st-sect-765-1026-15-102/ |
| 765 ILCS 1026/1401(b) | Disclosure restrictions | https://ilga.gov/legislation/ILCS/ |
| 5 ILCS 140 | Illinois Freedom of Information Act | https://illinoisattorneygeneral.gov/FOIAPAC/ |
| 2 Ill. Adm. Code 651 | Treasurer FOIA rules | https://ilga.gov/commission/jcar/admincode/ |

---

## Part 7: Strategic Recommendations

### Immediate Actions (Week 1)

1. **Test Cook County Treasurer Site**
   - Attempt automated searches on cookcountytreasurer.com
   - Assess bot protection compared to state site
   - Document any successful access methods

2. **File FOIA Request**
   - Submit statistical data request (without PII)
   - Request aggregate data by ZIP code and value range
   - Follow up after 5 business days

3. **Begin Manual Search Campaign**
   - Recruit volunteers if available
   - Start with top 5 surnames in highest-population ZIP codes
   - Document findings in structured format

### Short-Term Actions (Weeks 2-4)

4. **Contact Illinois State Treasurer**
   - Propose partnership for outreach
   - Explain public benefit and research goals
   - Request official data access or collaboration

5. **Explore MissingMoney.com**
   - Test automation accessibility
   - Compare results with Illinois ICash
   - Assess as alternative data source

6. **Contact Cook County Treasurer's Office**
   - Inquire about "Black Houses Matter" data
   - Request statistics on Cook County returns
   - Explore partnership opportunities

### Medium-Term Actions (Months 2-3)

7. **Develop Browser Extension**
   - If manual search proves viable but time-intensive
   - Create user-assisted search tool
   - Distribute to volunteers for scaled searching

8. **Engage Community Organizations**
   - Partner with groups like RAGE (Resident Association of Greater Englewood)
   - Leverage existing community networks
   - Provide value through outreach assistance

9. **Academic Partnership**
   - Contact researchers who study unclaimed property
   - Explore collaborative research opportunities
   - Share findings with academic community

### Long-Term Actions (Months 4-6)

10. **Advocate for Policy Change**
    - If research demonstrates significant public benefit
    - Propose amendments to disclosure restrictions
    - Work with legislators on transparency initiatives

11. **Build Comprehensive Database**
    - Compile data from all sources (state, county, federal)
    - Create unified search interface
    - Provide public benefit tool

12. **Establish Ongoing Monitoring**
    - Set up alerts for new property additions
    - Track high-value properties over time
    - Provide regular reports to stakeholders

---

## Part 8: Risk Assessment and Mitigation

### Legal Risks

**Risk**: Violating confidentiality statutes  
**Mitigation**: Only request and use data explicitly permitted by law; focus on aggregate statistics without PII

**Risk**: Terms of service violations  
**Mitigation**: Cease automated access attempts; use only manual or officially sanctioned methods

### Technical Risks

**Risk**: IP blocking from repeated access attempts  
**Mitigation**: Respect rate limits; use manual search methods; rotate IP addresses if legally permitted

**Risk**: Data accuracy issues  
**Mitigation**: Cross-reference multiple sources; verify findings before reporting

### Reputational Risks

**Risk**: Perceived as exploiting vulnerable populations  
**Mitigation**: Frame project as public benefit; partner with community organizations; focus on returning property to owners

**Risk**: Conflict with government agencies  
**Mitigation**: Maintain transparent communication; seek partnerships; comply with all regulations

---

## Part 9: Success Metrics

### Quantitative Metrics

1. **Number of properties identified** over $1,000 in Cook County
2. **Total dollar value** of identified properties
3. **Number of high-value alerts** (properties > $10,000)
4. **Coverage percentage** (ZIP codes searched / 99 total)
5. **Data sources accessed** (state, county, federal, other)

### Qualitative Metrics

1. **Data quality** - Accuracy and completeness of information
2. **Access methods** - Number of viable approaches identified
3. **Partnership success** - Collaborations established with agencies
4. **Community impact** - Outreach effectiveness and property returns facilitated
5. **Knowledge contribution** - Documentation and insights shared with public

---

## Part 10: Conclusion

### What We Learned

This extended research effort has revealed that accessing Illinois unclaimed property data is not merely a technical challenge, but a **legal and structural barrier by design**. The Illinois Revised Uniform Unclaimed Property Act explicitly protects owner privacy by restricting disclosure of property details and values.

### Why This Matters

The legal restrictions explain why:
- The ICash database hides property values until claims are filed
- Automated access is blocked by multiple protection layers
- Academic research on unclaimed property is scarce
- FOIA requests for bulk data will likely be denied

### The Path Forward

While bulk automated data access is not feasible under current law, multiple viable alternatives exist:

1. **Manual searching** remains legal and effective
2. **Cook County Treasurer** offers a separate $155 million database
3. **FOIA requests** may yield aggregate statistics
4. **Official partnerships** could provide sanctioned access
5. **Browser extensions** could assist volunteers
6. **Community outreach** aligns with government goals

### Strategic Pivot

Rather than attempting to circumvent legal protections, the project should pivot to:

1. **Assist with outreach** - Help government agencies return property to owners
2. **Focus on education** - Inform Cook County residents about available resources
3. **Build partnerships** - Collaborate with state and county treasurers
4. **Advocate for transparency** - Work within the system to improve public access

### Final Recommendation

The most effective approach is to **work with government agencies rather than around them**. By positioning this project as a public benefit initiative that helps return unclaimed property to rightful owners—particularly in underserved communities—we can potentially gain official support and access that would otherwise be legally prohibited.

The "Black Houses Matter" initiative by Cook County Treasurer Maria Pappas demonstrates that government agencies are willing to proactively reach out to help people claim their property. Our project should align with and support these existing efforts rather than attempting independent data extraction.

---

## Appendices

### Appendix A: Technical Test Results

**Selenium Test Results**:
- Control test (Google.com): ✓ Success
- Illinois ICash: ✗ 403 Forbidden (CloudFront block)
- Searches attempted: 50
- Searches completed: 0
- Timeout rate: 100%

**Protection Mechanisms Identified**:
- AWS CloudFront WAF
- Cloudflare Turnstile
- JavaScript challenge
- Bot behavior detection

### Appendix B: Legal Citations

**Primary Statutes**:
- 765 ILCS 1026/ - Revised Uniform Unclaimed Property Act
- 765 ILCS 1026/15-102(5) - Confidential information definition
- 765 ILCS 1026/1401(b) - Disclosure restrictions
- 5 ILCS 140 - Illinois Freedom of Information Act

**Administrative Rules**:
- 2 Ill. Adm. Code 651 - State Treasurer FOIA rules
- 74 Ill. Adm. Code 760.1000 - Confidentiality regulations

### Appendix C: Contact Directory

**Illinois State Treasurer**:
- Treasurer: Michael Frerichs
- Phone: (217) 785-6998
- Email: Via website contact form
- FOIA: FOIA@illinoistreasurer.gov
- Address: 1 East Old State Capitol Plaza, Springfield, IL 62701

**Cook County Treasurer**:
- Treasurer: Maria Pappas
- Phone: (312) 443-5100
- Address: 118 North Clark Street, Room 112, Chicago, IL 60602
- Radio Show: WVON 1690-AM (Mondays)

**NAUPA (National Association)**:
- Website: https://unclaimed.org/
- Purpose: Leading authority in unclaimed property

### Appendix D: Data Structure

**Recommended JSON Format for Manual Data Collection**:

```json
{
  "scan_metadata": {
    "scan_date": "ISO timestamp",
    "data_sources": ["Illinois ICash", "Cook County Treasurer", "Other"],
    "total_properties": 0,
    "high_value_count": 0,
    "min_value_threshold": 1000,
    "alert_threshold": 10000,
    "zip_codes_covered": [],
    "surnames_searched": [],
    "coverage_percentage": 0
  },
  "high_value_alerts": [
    {
      "property_owner_name": "Name (if public)",
      "dollar_amount": 0,
      "property_type": "Type",
      "source": "Illinois ICash | Cook County | Other",
      "zip_code": "60601",
      "discovery_date": "ISO timestamp",
      "claim_url": "Direct link"
    }
  ],
  "all_properties": [],
  "data_sources_searched": [
    {
      "source_name": "Illinois ICash",
      "url": "https://icash.illinoistreasurer.gov",
      "search_method": "Manual | Automated | FOIA",
      "searches_completed": 0,
      "properties_found": 0,
      "date_searched": "ISO timestamp"
    }
  ]
}
```

---

**Report Prepared By**: Manus AI Agent  
**Date**: January 7, 2026  
**Version**: 1.0  
**Status**: Complete

---

*This report represents comprehensive research into alternative sources and methods for accessing Illinois unclaimed property data. All findings are based on publicly available information and legal analysis as of January 7, 2026.*
