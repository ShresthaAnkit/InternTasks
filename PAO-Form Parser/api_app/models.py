from pydantic import BaseModel, Field
from typing import Optional, List

class IdentificationDetails(BaseModel):
    legal_id: Optional[str] = Field(None, description="Type of Legal ID (e.g., National Identity Card)")
    number_type: str = Field(..., description="Number or type of the ID")
    issuing_office: Optional[str] = Field(None, description="Issuing office of the ID")
    date_of_issue: str = Field(..., description="Date of issue (in YYYY-MM-DD format)")
    expiry_date: Optional[str] = Field(None, description="Expiry date (in YYYY-MM-DD format)")
    primary_secondary: Optional[str] = Field(None, description="Primary/Secondary designation")

class RelatedParty(BaseModel):
    relation: Optional[str] = Field(None, description="Relation (e.g., Father, Mother)")
    full_name: str = Field(..., description="Full name of the related party")
    id_type: Optional[str] = Field(None, description="Type of ID for the related party")
    id_no: Optional[str] = Field(None, description="ID number of the related party")
    have_account: Optional[str] = Field(None, description="Whether the related party has an account (Yes/No)")
    customer_no: Optional[str] = Field(None, description="Customer number if applicable")

class PersonalAccountForm(BaseModel):
    date: Optional[str] = Field(None, description="Form submission date (in YYYY-MM-DD format)")
    branch: Optional[str] = Field(None, description="Branch name")
    account_type: str = Field(..., description="Type of account (e.g., Saving, Current)")
    product_name: Optional[str] = Field(None, description="Name of the product, if applicable")
    currency: str = Field(..., description="Selected currency (e.g., NPR, USD)")
    salutation: Optional[str] = Field(None, description="Salutation (e.g., Mr., Ms.)")
    full_name: str = Field(..., description="Full name of the account holder")
    date_of_birth_bs: str = Field(..., description="Date of birth in B.S. format")
    date_of_birth_ad: str = Field(..., description="Date of birth in A.D. format")
    gender: str = Field(..., description="Gender (e.g., Male, Female, Others)")
    marital_status: str = Field(..., description="Marital status (e.g., Married, Unmarried)")
    nationality: str = Field(..., description="Nationality of the account holder")
    resident: Optional[str] = Field(None, description="Resident status, if applicable")
    education: Optional[str] = Field(None, description="Education level (e.g., Literate, Illiterate)")
    existing_account: str = Field(..., description="Whether the account holder has an existing account (Yes/No)")
    account_no: Optional[str] = Field(None, description="Existing account number, if applicable")
    identification_details: List[IdentificationDetails] = Field(..., description="List of identification details")
    related_parties: Optional[List[RelatedParty]] = Field(None, description="List of related parties")

