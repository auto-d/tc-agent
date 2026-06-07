# Agent Architecture with Tool Use Report

## Design 

The design doesn't deviate much from the template, with only two notable changes: 
1. We used an inherited method to generate tool schemas to standardize the way which those schemas are presented and stringified. This reduces the likelihood of inconsistencies as tool employment grows and reduces the chances of runtime surprises. 
2. Tool calling is built around the Gemini API expectations, in lieu of plain prompt stuffing. This trades some more structured overhead and redtape for smoother and more reliable tool calling.

## Test cases

### Travel Policy 

![alt text](image.png)

### Layoffs 

![alt text](image-1.png)

### Expense Limits

![alt text](image-2.png)

### Angela's Sales

![alt text](image-3.png)

### The Brians

![alt text](image-4.png)

### Danielle's Benefits

![alt text](image-5.png)

### Employee ID lookupg 

![alt text](image-6.png)

### 🏐 Wilson!!!

![alt text](image-7.png)

### PTO 

![alt text](image-8.png)

### Confidential!!

![alt text](image-9.png)

